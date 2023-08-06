from typing import Optional, Sequence, Tuple
from django.db import models
from django.contrib import admin
from django.utils.translation import pgettext_lazy, gettext_lazy as _

from ..models import UserCheck
from ..discovery import get_registry


__all__ = (
    'QuerySetChoicesFilter',
    'ReasonFilterBase',
    'ReasonDependentFilterMixin',
    'StateFilterBase',
    'create_dependent_filters',

    'AllReasonStatesFilterBase',
    'create_all_reason_state_filter',

    'IsReviewedFilterBase',
    'create_is_reviewed_filter',
)


class QuerySetChoicesFilter(admin.SimpleListFilter):
    lookup: str

    def get_lookup(self):
        return self.lookup

    def queryset(self, request, queryset):
        value = self.value()

        if value is None:
            return queryset

        return queryset.filter(**{self.get_lookup(): value})


class NonRemovableParametersFilterMixin:
    def __init__(self, request, params, model, model_admin):
        super().__init__(request, params, model, model_admin)

        if self.parameter_name in self.used_parameters:
            params[self.parameter_name] = self.used_parameters[self.parameter_name]


class ReasonFilterBase(NonRemovableParametersFilterMixin, QuerySetChoicesFilter):
    def lookups(self, request, model_admin):
        return get_registry().choices


class ReasonDependentFilterMixin(NonRemovableParametersFilterMixin, admin.ListFilter):
    exists_field_name: str
    reason_parameter_name: str
    reason_outer_ref: str

    def __init__(self, request, params, model, model_admin):
        super().__init__(request, params, model, model_admin)

        if self.reason_parameter_name in params:
            value = params.get(self.reason_parameter_name)
            self.used_parameters[self.reason_parameter_name] = value

    def reason_value(self):
        return self.used_parameters.get(self.reason_parameter_name)

    def expected_parameters(self):
        return super().expected_parameters() + [self.reason_parameter_name]


class StateFilterBase(QuerySetChoicesFilter, ReasonDependentFilterMixin):
    lookup: str = '_state_check_parameter_exists'

    def lookups(self, request, model_admin):
        reason = self.reason_value()
        registry = get_registry()

        if not reason or reason not in registry:
            return []

        return registry[reason].choices

    def queryset(self, request, queryset):
        value = self.value()
        reason_value = self.reason_value()

        if value is None or reason_value is None:
            return queryset

        lookup = self.get_lookup()

        return queryset.annotate(**{
            lookup: models.Exists(UserCheck.objects.filter(
                id=models.OuterRef(self.reason_outer_ref),
                state=value, reason=reason_value
            ))
        }).filter(**{lookup: True})


def create_dependent_filters(
    reason_parameter: str = 'reason',
    reason_lookup: str = 'reason',
    reason_title: Optional[str] = pgettext_lazy('wcd_user_checks', 'Reason'),
    state_parameter: str = 'state',
    state_title: Optional[str] = pgettext_lazy('wcd_user_checks', 'State'),
    state_reason_outer_ref: str = 'id',
):
    return {
        'reason': type('ReasonFilter', (ReasonFilterBase,), {
            'title': reason_title,
            'parameter_name': reason_parameter,
            'lookup': reason_lookup,
        }),
        'state': type('StateFilter', (StateFilterBase,), {
            'title': state_title,
            'parameter_name': state_parameter,
            'reason_parameter_name': reason_parameter,
            'reason_outer_ref': state_reason_outer_ref,
        }),
    }


def filter_state_queryset(
    queryset,
    outer_ref_field: str,
    outer_ref: str,
    lookup: str,
    values: Sequence[Tuple[str, str]],
    kwargs: dict = {}
):
    values = list(values)
    subquery = (
        UserCheck.objects
        .filter(**{outer_ref_field: models.OuterRef(outer_ref)})
    )
    whens = []

    if len(values) > 0:
        whens = (
            models.When(
                models.Q(state=state, reason=reason, **kwargs),
                then=models.Value(True)
            )
            for reason, state in values
        )
    elif len(kwargs.keys()) > 0:
        whens = (models.When(models.Q(**kwargs), then=models.Value(True)),)

    subquery = subquery.annotate(_is=models.Case(
        *whens,
        default=models.Value(False),
        output_field=models.BooleanField()
    ))
    queryset = (
        queryset
        .annotate(**{lookup: models.Exists(subquery.filter(_is=True))})
        .filter(**{lookup: True})
    )

    return queryset


class AllReasonStatesFilterBase(NonRemovableParametersFilterMixin, QuerySetChoicesFilter):
    outer_ref: str
    outer_ref_field: str
    delimiter: str = '::'
    lookup: str = '_state_check_parameter_exists'

    def lookups(self, request, model_admin):
        registry = get_registry()

        for reason, label in registry.choices:
            for state, state_label in registry[reason].choices:
                yield (
                    self.delimiter.join((reason, state)),
                    ': '.join((str(label), str(state_label)))
                )

    def queryset(self, request, queryset):
        value = self.value()

        if value is None:
            return queryset

        return filter_state_queryset(
            queryset, self.outer_ref_field, self.outer_ref, self.get_lookup(),
            [value.split(self.delimiter)]
        )


class AllReasonStatesMultiselectFilterBase(AllReasonStatesFilterBase):
    values_delimiter: str = ','

    def value(self):
        value = super().value()

        if value is None or value == '':
            return None

        return value.split(self.values_delimiter)

    def queryset(self, request, queryset):
        values = self.value()

        if values is None:
            return queryset

        return filter_state_queryset(
            queryset, self.outer_ref_field, self.outer_ref, self.get_lookup(),
            (item.split(self.delimiter) for item in values)
        )

    def choices(self, changelist):
        values = self.value()

        yield {
            'selected': values is None,
            'query_string': changelist.get_query_string(remove=[self.parameter_name]),
            'display': _('All'),
        }

        values = set(values or {})

        for lookup, title in self.lookup_choices:
            selected = lookup in values
            vals = (values - {lookup}) if selected else (values | {lookup})

            yield {
                'selected': selected,
                'query_string': changelist.get_query_string({self.parameter_name: self.values_delimiter.join(vals)}),
                'display': title,
            }


def create_all_reason_state_filter(
    parameter: str = 'state',
    outer_ref: str = 'id',
    outer_ref_field: str = 'id',
    title: Optional[str] = pgettext_lazy('wcd_user_checks', 'State'),
):
    return type('AllReasonStatesFilter', (AllReasonStatesMultiselectFilterBase,), {
        'title': title,
        'parameter_name': parameter,
        'outer_ref': outer_ref,
        'outer_ref_field': outer_ref_field,
    })


class IsReviewedFilterBase(admin.BooleanFieldListFilter):
    state_parameter_name: str
    outer_ref: str
    outer_ref_field: str
    delimiter: str = '::'
    lookup: str = '_state_with_reviewed_check_parameter_exists'
    values_delimiter: str = ','

    def __init__(self, field, request, params, model, model_admin, field_path):
        super().__init__(field, request, params, model, model_admin, field_path)

        if self.state_parameter_name in params:
            value = params.get(self.state_parameter_name)
            self.used_parameters[self.state_parameter_name] = value

    def state_value(self):
        val = self.used_parameters.get(self.state_parameter_name)

        if not val:
            return None

        return val.split(self.values_delimiter)

    def expected_parameters(self):
        return super().expected_parameters() + [self.state_parameter_name]

    def get_lookup(self):
        return self.lookup

    def queryset(self, request, queryset):
        value = self.used_parameters.get(self.lookup_kwarg)
        state_values = self.state_value()

        if value is None:
            return queryset

        args = (
            queryset, self.outer_ref_field, self.outer_ref, self.get_lookup(),
        )
        kwargs = {'is_reviewed': value}

        if not state_values:
            return filter_state_queryset(*args, [], kwargs)

        return filter_state_queryset(
            *args,
            (item.split(self.delimiter) for item in state_values),
            kwargs
        )


def create_is_reviewed_filter(
    state_parameter: str = 'state__in',
    outer_ref: str = 'id',
    outer_ref_field: str = 'id',
):
    return type('IsReviewedFilter', (IsReviewedFilterBase,), {
        'state_parameter_name': state_parameter,
        'outer_ref': outer_ref,
        'outer_ref_field': outer_ref_field,
    })
