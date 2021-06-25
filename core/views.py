
from rest_framework.response import Response
from core.models import Post
from core.serializers import PostSerializer, RegisterSerializer, LoginSerializers
from rest_framework import generics
from django.contrib.auth.models import User, update_last_login
from core.serializers import UserSerializer
from rest_framework import permissions
from core.permissions import IsOwnerOrReadOnly
from rest_framework.decorators import api_view
from rest_framework.reverse import reverse

from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework import status


class RegisterAPI(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
        "user": UserSerializer(user, context=self.get_serializer_context()).data,
        })


# class Login(APIView):
#     permission_classes = (AllowAny,)

#     def post(self,request):
#         email = request.data.get('email',None)
#         password = request.data.get('password',None)
#         if email and password:
#             user_obj = Account.objects.filter(email__iexact=email)
#             if user.exists() and user.first().check_password(password):
#                 user = UserLoginSerializer(user_obj)
#                 data_list = {}
#                 data_list.update(user.data)
#                 return Response({"message": "Login Successfully", "data":data_list, "code": 200})
#             else:
#                 message = "Unable to login with given credentials"
#                 return Response({"message": message , "code": 500, 'data': {}} )
#         else:
#             message = "Invalid login details."
#             return Response({"message": message , "code": 500, 'data': {}})


# @api_view(['POST,'])
# def login_view(request):

#     if request.method == 'POST':
#         serializer = LoginSerializer(data=request.data)
#         data = {}
#         if serializer.is_valid():
#             data['response'] = 'User successfully Login'
#         else:
#             data['response'] = 'You have entered an invalid username or password'
#         return Response(data)


class LoginAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializers(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        update_last_login(None, user)
        token, created = Token.objects.get_or_create(user=user)
        return Response({"status": status.HTTP_200_OK, "Token": token.key})


@api_view(['GET','POST'])
def api_root(request, format=None):
    return Response({
        'users': reverse('user-list', request=request, format=format),
        'posts': reverse('post-list', request=request, format=format)
    })

class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class UserDetail(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class PostList(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class PostDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    

