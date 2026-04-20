from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response

from web.models.character import Character


class HomepageIndexView(APIView):
    def get(self, request):
        try:
            items_count = int(request.query_params.get('items_count', 0))
            search_query = request.query_params.get('search_query', '')
            ###
            # 可优化部分：如果数据量很大，即items_count很大，那么每次查询都要扫描大量数据。
            # 游标分页：可以通过前端传入最后一个character的id，然后从小于当前id的开始查询数据库就好了（因为是降序）
            ###
            if search_query:
                ###
                # 可优化：MySQl + 全文索引；或者引入Elasticsearch、Meilisearch 或 Whoosh，将搜索和分页都委托给搜索引擎。
                ###
                queryset = Character.objects.filter(
                    Q(name__icontains=search_query) | Q(profile__icontains=search_query)
                )
            else:
                queryset = Character.objects.all()
            characters_raw = queryset.order_by('-id')[items_count : items_count + 20]
            characters = []
            for character in characters_raw:
                author = character.author
                characters.append({
                    'id': character.id,
                    'name': character.name,
                    'profile': character.profile,
                    'photo': character.photo.url,
                    'background_image': character.background_image.url,
                    'author': {
                        'user_id': author.user_id,
                        'username': author.user.username,
                        'photo': author.photo.url,
                    }
                })
            return Response({
                'result': 'success',
                'characters': characters,
            })
        except:
            return Response({
                'result': '系统异常，请稍后再试'
            })