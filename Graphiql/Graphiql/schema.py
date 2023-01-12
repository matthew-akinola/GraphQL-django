import graphene
from authentication.schema import  Mutation as AuthMutation, Query


class Mutation(AuthMutation, graphene.ObjectType):
   pass
schema = graphene.Schema(mutation=Mutation, query=Query)