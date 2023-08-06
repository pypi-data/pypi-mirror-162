import random

import obapi.export
from django.apps import apps
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.http import (
    Http404,
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseRedirect,
)
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_GET, require_POST
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
    View,
)
from django.views.generic.edit import FormMixin
from haystack.generic_views import SearchView
from haystack.query import EmptySearchQuerySet
from obapi.models import EssayContentItem, OBContentItem, YoutubeContentItem

from obpages.forms import (
    DefaultSearchForm,
    SequenceChangeForm,
    SequenceExportForm,
    SequenceMemberMoveForm,
    UserSequenceMemberAddForm,
)
from obpages.models import FeedbackNote, User, UserSequence, UserSequenceMember

OBPAGES_PAGES_PATH = "obpages"

RESULTS_PER_PAGE = getattr(settings, "OBPAGES_RESULTS_PER_PAGE", 20)
RESULTS_PER_SECTION = getattr(settings, "OBPAGES_RESULTS_PER_SECTION", 5)


@require_GET
def home(request):
    # TODO: put this data in the database
    curated_obcontentitem_ids = [
        "2017/02/neglected-big-problems",
        "2010/10/two-types-of-people",
        "2011/07/making-up-opinions",
        "2009/09/this-is-the-dream-time",
        "2010/03/further-than-africa",
        "2006/11/beware_heritabl",
    ]
    curated_essaycontentitem_ids = [
        "futarchy",
        "buyhealth",
        "innocence",
        "belieflikeclothes",
        "wouldhavebanned",
        "Lifeinsim",
    ]
    curated_youtubecontentitem_ids = [
        "4yZKGbq1YmA",  # intro to prediction markets
        "aspMV6ERqpo",  # great filter (TED)
        # "izEUig9w1tM", # vouching (TED)
        "l3whaviTqqg",  # grabby aliens animation
        "eK5qxAA60PQ",  # age of em
        "nIRvNxykvTQ",  # effective altruism
        # "aagyRGKv66g", # Dwarkesh interview
        "3tcYQE1B588",  # interview at Oxford
    ]
    context = {
        "title": "Home",
        "max_results": 6,
        "curated_essaycontentitems": EssayContentItem.objects.filter(
            item_id__in=curated_essaycontentitem_ids
        ),
        "curated_obcontentitems": OBContentItem.objects.filter(
            item_id__in=curated_obcontentitem_ids
        ),
        "curated_youtubecontentitems": YoutubeContentItem.objects.filter(
            item_id__in=curated_youtubecontentitem_ids
        ),
    }
    return render(request, f"{OBPAGES_PAGES_PATH}/home.html", context)


@require_GET
def about(request):
    context = {"title": "About this site"}
    return render(request, f"{OBPAGES_PAGES_PATH}/about.html", context)


class FeedbackView(CreateView):
    template_name = f"{OBPAGES_PAGES_PATH}/feedback.html"
    model = FeedbackNote
    fields = ("feedback",)
    extra_context = {"title": "Feedback Form"}

    def post(self, request):
        if request.user.is_authenticated:
            self.object = self.model(user=request.user)
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_form(self, form_class=None):
        form = super().get_form(form_class=form_class)
        placeholders = [
            "Everything sucks...",
            "The UI is terrible...",
            "The website is broken...",
        ]
        form.fields["feedback"].widget.attrs["placeholder"] = random.choice(
            placeholders
        )
        return form

    def get_success_url(self):
        """Return the URL to redirect to after processing a valid form."""
        return reverse("feedback_done")


@require_GET
def feedback_done(request):
    context = {"title": "Feedback Submitted Successfully"}
    return render(request, f"{OBPAGES_PAGES_PATH}/feedback_done.html", context)


class ContentSearchView(SearchView):
    template_name = f"{OBPAGES_PAGES_PATH}/search.html"
    form_class = DefaultSearchForm
    context_object_name = "search_results"
    extra_context = {"title": "Search"}

    def form_invalid(self, form):
        # Do not show results for invalid form
        context = self.get_context_data(
            **{self.form_name: form, "object_list": EmptySearchQuerySet()}
        )
        return self.render_to_response(context)


@require_GET
def explore_base(request):
    context = {"title": "Explore", "max_results": RESULTS_PER_SECTION}
    return render(request, f"{OBPAGES_PAGES_PATH}/explore_base.html", context)


@require_GET
def content_detail(request, item_source, item_id):
    item_type = f"{item_source}contentitem"
    item_model = apps.get_model("obapi", item_type)
    item = get_object_or_404(item_model, item_id=item_id)
    context = {
        "title": item.title,
        "item": item,
        "max_results": RESULTS_PER_SECTION,
    }
    if request.user.is_authenticated:
        context.update(
            {
                "sequencemember_add_url": reverse(
                    f"{item_type}_sequence_add",
                    kwargs={"item_source": item_source, "item_id": item_id},
                ),
                "sequencemember_add_form": UserSequenceMemberAddForm(user=request.user),
            }
        )
    return render(request, f"{OBPAGES_PAGES_PATH}/content_detail.html", context)


@require_POST
@login_required
def sequence_add_view(request, item_source, item_id):
    item_model = apps.get_model("obapi", f"{item_source}contentitem")
    content_item = get_object_or_404(item_model, item_id=item_id)

    initial_member = UserSequenceMember(content_item=content_item)
    form = UserSequenceMemberAddForm(
        user=request.user, data=request.POST, instance=initial_member
    )
    if form.is_valid():
        saved_member = form.save()
        sequence = saved_member.sequence
        success_url = reverse(
            "sequence_update",
            kwargs={"user_slug": request.user.slug, "sequence_slug": sequence.slug},
        )
        return HttpResponseRedirect(success_url)
    else:
        raise Http404("Specified Sequence not found for current User")


@require_GET
def explore_detail(request, model_name, instance_name):
    # Get model instance or return 404
    model_class = apps.get_model("obapi", model_name)
    model_instance = get_object_or_404(model_class, alias__text__iexact=instance_name)

    if instance_name != model_instance.slug:
        return redirect(
            "explore_detail",
            model_name=model_name,
            instance_name=model_instance.slug,
            permanent=True,
        )

    context = {
        "title": model_instance.name,
        "item": model_instance,
        "max_results": RESULTS_PER_SECTION,
    }
    return render(request, f"{OBPAGES_PAGES_PATH}/explore_detail.html", context)


class ExploreListView(ListView):
    template_name = f"{OBPAGES_PAGES_PATH}/explore_list.html"
    paginate_by = RESULTS_PER_PAGE
    context_object_name = "query_results"

    def get(self, request, model_name):
        self.model = apps.get_model("obapi", model_name)
        return super().get(request)

    def get_queryset(self):
        """Return the list of items for this view."""
        # Initial queryset
        queryset = self.model._default_manager.all()
        # Sort by item counts
        queryset = queryset.annotate(item_count=Count("content")).order_by(
            "-item_count"
        )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        title = self.model._meta.verbose_name_plural.title()
        context.update({"max_results": RESULTS_PER_SECTION, "title": title})
        return context


@require_GET
def sequence_base(request):
    context = {
        "title": "Sequences",
        "max_results": RESULTS_PER_SECTION,
    }
    return render(request, f"{OBPAGES_PAGES_PATH}/sequence_base.html", context)


class SequenceCreateView(LoginRequiredMixin, CreateView):
    template_name = f"{OBPAGES_PAGES_PATH}/sequence_create.html"
    model = UserSequence
    form_class = SequenceChangeForm
    extra_context = {"title": "Create Sequence"}

    def post(self, request, *args, **kwargs):
        self.object = self.model(owner=request.user)
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_success_url(self):
        return reverse(
            "sequence_detail",
            kwargs={
                "user_slug": self.object.owner.slug,
                "sequence_slug": self.object.slug,
            },
        )


class SequenceUserListView(ListView):
    template_name = f"{OBPAGES_PAGES_PATH}/sequence_list.html"
    paginate_by = RESULTS_PER_PAGE
    model = UserSequence
    context_object_name = "sequences"

    def get_queryset(self):
        if self.queryset is not None:
            return self.queryset

        owner_slug = self.kwargs.get("user_slug")
        all_sequences = self.model.objects.filter(owner__slug=owner_slug)

        if self.request.user.is_authenticated and self.request.user.slug == owner_slug:
            return all_sequences

        public_sequences = all_sequences.filter(public=True)
        return public_sequences

    def get_context_data(self, **kwargs):
        owner_slug = self.kwargs.get("user_slug")
        if self.request.user.is_authenticated and self.request.user.slug == owner_slug:
            title = "Your Sequences"
        else:
            owner = User.objects.get(slug=owner_slug)
            title = f"{owner}'s Sequences"

        kwargs.update({"title": title})
        return super().get_context_data(**kwargs)


class SequenceCuratedListView(ListView):
    template_name = f"{OBPAGES_PAGES_PATH}/sequence_list.html"
    paginate_by = RESULTS_PER_PAGE
    model = UserSequence
    context_object_name = "sequences"
    extra_context = {"title": "Curated Sequences"}

    def get_queryset(self):
        if self.queryset is not None:
            return self.queryset

        return self.model.objects.filter(curated=True)


class SequencePublicListView(ListView):
    template_name = f"{OBPAGES_PAGES_PATH}/sequence_list.html"
    paginate_by = RESULTS_PER_PAGE
    model = UserSequence
    context_object_name = "sequences"
    extra_context = {"title": "User-Created Sequences"}

    def get_queryset(self):
        if self.queryset is not None:
            return self.queryset

        return self.model.objects.filter(public=True)


class SequenceDetailView(DetailView):
    template_name = f"{OBPAGES_PAGES_PATH}/sequence_detail.html"
    slug_url_kwarg = "sequence_slug"
    context_object_name = "sequence"

    def get_queryset(self):
        if self.queryset is not None:
            return self.queryset.all()

        # Get sequences for user
        owner_slug = self.kwargs.get("user_slug")
        all_sequences = UserSequence.objects.filter(owner__slug=owner_slug)

        # If current user is owner, display all sequences
        if self.request.user.is_authenticated and self.request.user.slug == owner_slug:
            return all_sequences

        # Otherwise display only public sequences
        public_sequences = all_sequences.filter(public=True)
        return public_sequences

    def get_context_data(self, **kwargs):

        kwargs.update(
            **{
                "title": self.object.title,
                "owner": self.object.owner,
                "export_form": SequenceExportForm(),
                "user_is_owner": self.request.user == self.object.owner,
            }
        )
        return super().get_context_data(**kwargs)


@require_GET
def sequence_export_view(request, user_slug, sequence_slug):
    # Get object or 404
    sequence = get_object_or_404(
        UserSequence, owner__slug=user_slug, slug=sequence_slug
    )

    # Check user is authorised to access the Sequence
    if not sequence.public and sequence.owner != request.user:
        raise Http404

    # Construct form
    form = SequenceExportForm(data=request.GET)
    if form.is_valid():
        writer = form.cleaned_data["writer"]()
        result = obapi.export.export_sequence(sequence, writer)
        return HttpResponse(
            result,
            headers={
                "Content-Type": writer.mime_type,
                "Content-Disposition": (
                    f'attachment; filename="{sequence.slug}{writer.file_suffix}"'
                ),
            },
        )
    else:
        return HttpResponseBadRequest()


class SequenceUpdateView(LoginRequiredMixin, UpdateView):
    template_name = f"{OBPAGES_PAGES_PATH}/sequence_update.html"
    model = UserSequence
    form_class = SequenceChangeForm
    context_object_name = "sequence"
    extra_context = {"title": "Edit Sequence"}

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        if "_delete" in request.POST:
            user_slug = self.object.owner.slug
            sequence_slug = self.object.slug
            return redirect(
                "sequence_delete", user_slug=user_slug, sequence_slug=sequence_slug
            )

        if "_saveasnew" in request.POST:
            # Create new Sequence object with current user as owner
            self.object = self.model(owner=request.user)

        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_object(self, queryset=None):
        sequence_slug = self.kwargs.get("sequence_slug")
        return get_object_or_404(
            self.model, owner=self.request.user, slug=sequence_slug
        )

    def get_success_url(self):
        return reverse(
            "sequence_detail",
            kwargs={
                "user_slug": self.object.owner.slug,
                "sequence_slug": self.object.slug,
            },
        )


class SequenceDeleteView(LoginRequiredMixin, DeleteView):
    template_name = f"{OBPAGES_PAGES_PATH}/sequence_delete.html"
    model = UserSequence
    context_object_name = "sequence"
    extra_context = {"title": "Delete Sequence"}

    def get_object(self, queryset=None):
        sequence_slug = self.kwargs.get("sequence_slug")
        return get_object_or_404(
            self.model, owner=self.request.user, slug=sequence_slug
        )

    def get_success_url(self):
        user_slug = self.kwargs.get("user_slug")
        return reverse("sequence_user_list", kwargs={"user_slug": user_slug})


class SequenceMemberMoveView(FormMixin, View):
    form_class = SequenceMemberMoveForm

    def post(self, request, user_slug, sequence_slug, order):
        """
        Handle POST requests: instantiate a form instance with the passed
        POST variables and then check if it's valid.
        """
        self.object = self.get_object()
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_object(self):
        if hasattr(self, "object"):
            return self.object
        else:
            return get_object_or_404(
                UserSequenceMember,
                sequence__owner__slug=self.kwargs.get("user_slug"),
                sequence__slug=self.kwargs.get("sequence_slug"),
                order=self.kwargs.get("order"),
            )

    def get_success_url(self):
        """Return the URL to redirect to after processing a valid form."""
        sequence = self.object.sequence
        return reverse(
            "sequence_update",
            kwargs={
                "user_slug": sequence.owner.slug,
                "sequence_slug": sequence.slug,
            },
        )

    def form_valid(self, form):
        """If the form is valid, perform the requested action."""
        member = self.object
        action_choices = {
            "top": member.top,
            "up": member.up,
            "down": member.down,
            "bottom": member.bottom,
        }

        action = form.cleaned_data["move"]

        if action in action_choices.keys():
            action_choices[action]()
            return HttpResponseRedirect(self.get_success_url())
        else:
            raise Http404

    def form_invalid(self, form):
        """If the form is invalid, return a 404 error message."""
        raise Http404


@require_POST
def sequencemember_delete_view(request, user_slug, sequence_slug, order):
    sequence_member = get_object_or_404(
        UserSequenceMember,
        sequence__owner__slug=user_slug,
        sequence__slug=sequence_slug,
        order=order,
    )
    success_url = reverse(
        "sequence_update",
        kwargs={
            "user_slug": sequence_member.sequence.owner.slug,
            "sequence_slug": sequence_member.sequence.slug,
        },
    )
    sequence_member.delete()
    return HttpResponseRedirect(success_url)


class UserDetailView(DetailView):
    template_name = f"{OBPAGES_PAGES_PATH}/user_detail.html"
    slug_url_kwarg = "user_slug"
    model = User
    context_object_name = "displayed_user"

    def get_context_data(self, **kwargs):
        kwargs = super().get_context_data(**kwargs)
        kwargs["title"] = f"{self.object.username}'s profile"
        return kwargs
