from rest_framework import viewsets

from .models import ScoringRule
from .serializers import ScoringRuleSerializer


class ScoringRuleViewSet(viewsets.ModelViewSet):
    queryset = ScoringRule.objects.all()
    serializer_class = ScoringRuleSerializer
    filterset_fields = ('competition',)
