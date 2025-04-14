from rest_framework import viewsets, mixins
from django.shortcuts import get_object_or_404
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter

from .serializers import (PostSerializer, GroupSerializer,
                          CommentSerializer, FollowSerializer)
from posts.models import Post, Group, Comment
from .permissions import IsAuthor
# Create your views here.


@permission_classes([IsAuthor])
class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


class GroupViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer


@permission_classes([IsAuthor])
class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def get_post(self):
        """Возвращает объект текущей записи."""
        post_id = self.kwargs.get('post_id')
        return get_object_or_404(Post, pk=post_id)

    def get_queryset(self):
        """Возвращает queryset c комментариями для текущей записи."""
        return self.get_post().comments.all()

    def perform_create(self, serializer):
        """Создает комментарий для текущего поста,
        где автором является текущий пользователь."""
        post_id = self.kwargs.get('post_id')
        post = get_object_or_404(Post, pk=post_id)
        serializer.save(
            author=self.request.user,
            post=post
        )


class FollowViewSet(mixins.CreateModelMixin,
                    mixins.ListModelMixin,
                    viewsets.GenericViewSet):
    serializer_class = FollowSerializer
    permission_classes = (IsAuthenticated, )
    filter_backends = (SearchFilter, )
    search_fields = ('following__username', )

    def get_queryset(self):
        return self.request.user.follower.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
