from django.urls import include, path, register_converter

from . import converters, views

register_converter(converters.YoutubeVideoIDConverter, "youtube_id")
register_converter(converters.SpotifyEpisodeIDConverter, "spotify_id")
register_converter(converters.OBPostNameConverter, "ob_name")
register_converter(converters.EssayIDConverter, "essay_id")
register_converter(converters.ClassifierNameConverter, "classifier")
urlpatterns = [
    # select2 widgets
    path("select2/", include("django_select2.urls")),
    # Search
    path("", views.home, name="home"),
    path("about", views.about, name="about"),
    path("feedback", views.FeedbackView.as_view(), name="feedback"),
    path("feedback/done", views.feedback_done, name="feedback_done"),
    path("search", views.ContentSearchView.as_view(), name="search"),
    # Account
    path("", include("obpages.accounts.urls")),
    # Content
    path(
        "content/youtube/<youtube_id:item_id>",
        views.content_detail,
        {"item_source": "youtube"},
        name="youtubecontentitem_detail",
    ),
    path(
        "content/spotify/<spotify_id:item_id>",
        views.content_detail,
        {"item_source": "spotify"},
        name="spotifycontentitem_detail",
    ),
    path(
        "content/overcomingbias/<ob_name:item_id>",
        views.content_detail,
        {"item_source": "ob"},
        name="obcontentitem_detail",
    ),
    path(
        "content/essays/<essay_id:item_id>",
        views.content_detail,
        {"item_source": "essay"},
        name="essaycontentitem_detail",
    ),
    path(
        "content/youtube/<youtube_id:item_id>/sequences/add",
        views.sequence_add_view,
        {"item_source": "youtube"},
        name="youtubecontentitem_sequence_add",
    ),
    path(
        "content/spotify/<spotify_id:item_id>/sequences/add",
        views.sequence_add_view,
        {"item_source": "spotify"},
        name="spotifycontentitem_sequence_add",
    ),
    path(
        "content/overcomingbias/<ob_name:item_id>/sequences/add",
        views.sequence_add_view,
        {"item_source": "ob"},
        name="obcontentitem_sequence_add",
    ),
    path(
        "content/essays/<essay_id:item_id>/sequences/add",
        views.sequence_add_view,
        {"item_source": "essay"},
        name="essaycontentitem_sequence_add",
    ),
    # Explore
    path("explore", views.explore_base, name="explore_base"),
    path(
        "explore/<classifier:model_name>",
        views.ExploreListView.as_view(),
        name="explore_list",
    ),
    path(
        "explore/<classifier:model_name>/<str:instance_name>",
        views.explore_detail,
        name="explore_detail",
    ),
    # Sequences
    path("sequences", views.sequence_base, name="sequence_base"),
    path(
        "sequences/curated",
        views.SequenceCuratedListView.as_view(),
        name="sequence_curated_list",
    ),
    path(
        "sequences/public",
        views.SequencePublicListView.as_view(),
        name="sequence_public_list",
    ),
    path(
        "sequences/create", views.SequenceCreateView.as_view(), name="sequence_create"
    ),
    # User pages
    path("users/<str:user_slug>", views.UserDetailView.as_view(), name="user_detail"),
    path(
        "users/<str:user_slug>/sequences",
        views.SequenceUserListView.as_view(),
        name="sequence_user_list",
    ),
    path(
        "users/<str:user_slug>/sequences/<str:sequence_slug>",
        views.SequenceDetailView.as_view(),
        name="sequence_detail",
    ),
    path(
        "users/<str:user_slug>/sequences/<str:sequence_slug>/edit",
        views.SequenceUpdateView.as_view(),
        name="sequence_update",
    ),
    path(
        "users/<str:user_slug>/sequences/<str:sequence_slug>/delete",
        views.SequenceDeleteView.as_view(),
        name="sequence_delete",
    ),
    path(
        "users/<str:user_slug>/sequences/<str:sequence_slug>/export",
        views.sequence_export_view,
        name="sequence_export",
    ),
    path(
        "users/<str:user_slug>/sequences/<str:sequence_slug>"
        "/sequencemembers/<int:order>/move",
        views.SequenceMemberMoveView.as_view(),
        name="sequencemember_move",
    ),
    path(
        "users/<str:user_slug>/sequences/<str:sequence_slug>"
        "/sequencemembers/<int:order>/delete",
        views.sequencemember_delete_view,
        name="sequencemember_delete",
    ),
]
