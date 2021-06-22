from swampdragon.serializers.model_serializer import ModelSerializer


class NotificationSerializer(ModelSerializer):

    class Meta:
        model = 'friends.Notification'
        publish_fields = ['message', 'skigit_id','from_user', 'is_read',
                          'msg_type', 'create_date',]
