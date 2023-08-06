import graphene
from graphene_django import DjangoObjectType
from graphene_django.forms.mutation import DjangoModelFormMutation

from .forms import PersonForm
from .models import Group, Notification, Person
from .util.core_helpers import get_app_module, get_app_packages, has_person


class NotificationType(DjangoObjectType):
    class Meta:
        model = Notification


class PersonType(DjangoObjectType):
    class Meta:
        model = Person

    full_name = graphene.Field(graphene.String)

    def resolve_full_name(root: Person, info, **kwargs):
        return root.full_name


class GroupType(DjangoObjectType):
    class Meta:
        model = Group


class PersonMutation(DjangoModelFormMutation):
    person = graphene.Field(PersonType)

    class Meta:
        form_class = PersonForm


class MarkNotificationReadMutation(graphene.Mutation):
    class Arguments:
        id = graphene.ID()  # noqa

    notification = graphene.Field(NotificationType)

    @classmethod
    def mutate(cls, root, info, id):  # noqa
        notification = Notification.objects.get(pk=id)
        # FIXME permissions
        notification.read = True
        notification.save()

        return notification


class Query(graphene.ObjectType):
    ping = graphene.String(default_value="pong")

    notifications = graphene.List(NotificationType)

    persons = graphene.List(PersonType)
    person_by_id = graphene.Field(PersonType, id=graphene.ID())
    who_am_i = graphene.Field(PersonType)

    def resolve_notifications(root, info, **kwargs):
        # FIXME do permission stuff
        return Notification.objects.all()

    def resolve_persons(root, info, **kwargs):
        # FIXME do permission stuff
        return Person.objects.all()

    def resolve_person_by_id(root, info, id):  # noqa
        return Person.objects.get(pk=id)

    def resolve_who_am_i(root, info, **kwargs):
        if has_person(info.context.user):
            return info.context.user.person
        else:
            return None


class Mutation(graphene.ObjectType):
    update_person = PersonMutation.Field()

    mark_notification_read = MarkNotificationReadMutation.Field()


def build_global_schema():
    """Build global GraphQL schema from all apps."""
    query_bases = [Query]
    mutation_bases = [Mutation]

    for app in get_app_packages():
        schema_mod = get_app_module(app, "schema")
        if not schema_mod:
            # The app does not define a schema
            continue

        if AppQuery := getattr(schema_mod, "Query", None):
            query_bases.append(AppQuery)
        if AppMutation := getattr(schema_mod, "Mutation", None):
            mutation_bases.append(AppMutation)

    # Define classes using all query/mutation classes as mixins
    #  cf. https://docs.graphene-python.org/projects/django/en/latest/schema/#adding-to-the-schema
    GlobalQuery = type("GlobalQuery", tuple(query_bases), {})
    GlobalMutation = type("GlobalMutation", tuple(mutation_bases), {})

    return graphene.Schema(query=GlobalQuery, mutation=GlobalMutation)


schema = build_global_schema()
