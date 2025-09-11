from typing import Literal

from pydantic import Field

from pydantic_gerrit.base import BaseModelGerrit


# The DiffIntralineInfo entity contains information about intraline edits in a file.
#
# The information consists of a list of <skip length, edit length> pairs, where the skip length is
# the number of characters between the end of the previous edit and the start of this edit, and the
# edit length is the number of edited characters following the skip. The start of the edits is from
# the beginning of the related diff content lines. If the list is empty, the entire DiffContent
# should be considered as unedited.
#
# Note that the implied newline character at the end of each line is included in the length
# calculation, and thus it is possible for the edits to span newlines.
#
# https://gerrit-review.googlesource.com/Documentation/rest-api-changes.html#diff-intraline-info
#
SkipLength = int
EditLength = int
DiffIntralineInfo = tuple[SkipLength, EditLength]


class DiffContent(BaseModelGerrit):
    """
    The DiffContent entity contains information about the content differences in a file.

    https://gerrit-review.googlesource.com/Documentation/rest-api-changes.html#diff-content
    """

    a: list[str] | None = Field(
        default=None,
        description='Content only in the file on side A (deleted in B).',
    )
    b: list[str] | None = Field(
        default=None,
        description='Content only in the file on side B (added in B).',
    )
    ab: list[str] | None = Field(
        default=None,
        description='Content in the file on both sides (unchanged).',
    )
    edit_a: 'DiffIntralineInfo | None' = Field(
        default=None,
        description='Text sections deleted from side A as a DiffIntralineInfo entity. (only present when the `intraline` parameter is set and the DiffContent is a replace, i.e. both `a` and `b` are present)',
    )
    edit_b: 'DiffIntralineInfo | None' = Field(
        default=None,
        description='Text sections inserted in side B as a DiffIntralineInfo entity. (only present when the `intraline` parameter is set and the DiffContent is a replace, i.e. both `a` and `b` are present)',
    )
    due_to_rebase: bool | None = Field(
        default=None,
        description='Indicates whether this entry was introduced by a rebase. (not set if false)',
    )
    due_to_move: bool | None = Field(
        default=None,
        description='Indicates whether this entry was introduced by a move operation. (not set if false)',
    )
    skip: int | None = Field(
        default=None,
        description='Count of lines skipped on both sides when the file is too large to include all common lines.',
    )
    common: bool | None = Field(
        default=None,
        description='Set to true if the region is common according to the requested ignore-whitespace parameter, but a and b contain differing amounts of whitespace. When present and true a and b are used instead of ab.',
    )


class DiffFileMetaInfo(BaseModelGerrit):
    """
    The DiffFileMetaInfo entity contains meta information about a file diff.

    https://gerrit-review.googlesource.com/Documentation/rest-api-changes.html#diff-file-meta-info
    """

    name: str = Field(
        description='The name of the file.',
    )
    content_type: str = Field(
        description='The content type of the file. For the commit message and merge list the value is text/x-gerrit-commit-message and text/x-gerrit-merge-list respectively. For git links the value is x-git/gitlink. For symlinks the value is x-git/symlink. For regular files the value is the file mime type (e.g. text/x-java, text/x-c++src, etc.).',
    )
    lines: int = Field(
        description='The total number of lines in the file.',
    )
    web_links: list['WebLinkInfo'] | None = Field(
        default=None,
        description='Links to the file in external sites as a list of WebLinkInfo entries.',
    )


class DiffInfo(BaseModelGerrit):
    """
    The DiffInfo entity contains information about the diff of a file in a revision.

    If the weblinks-only parameter is specified, only the web_links field is set.

    https://gerrit-review.googlesource.com/Documentation/rest-api-changes.html#diff-info
    """

    meta_a: DiffFileMetaInfo | None = Field(
        default=None,
        description='Meta information about the file on side A as a DiffFileMetaInfo entity. (not present when the file is added)',
    )
    meta_b: DiffFileMetaInfo | None = Field(
        default=None,
        description='Meta information about the file on side B as a DiffFileMetaInfo entity. (not present when the file is deleted)',
    )
    change_type: Literal['ADDED', 'MODIFIED', 'DELETED', 'RENAMED', 'COPIED', 'REWRITE'] = Field(
        description='The type of change',
    )
    intraline_status: Literal['OK', 'ERROR', 'TIMEOUT'] | None = Field(
        default=None,
        description='Intraline status. (only set when the intraline parameter was specified in the request)',
    )
    diff_header: list[str] = Field(
        description='A list of strings representing the patch set diff header.',
    )
    content: list[DiffContent] = Field(
        description='The content differences in the file as a list of DiffContent entities.',
    )
    web_links: list['DiffWebLinkInfo'] | None = Field(
        default=None,
        description='Links to the file diff in external sites as a list of DiffWebLinkInfo entries.',
    )
    edit_web_links: list['WebLinkInfo'] | None = Field(
        default=None,
        description='Links to edit the file in external sites as a list of WebLinkInfo entries.',
    )
    binary: bool | None = Field(
        default=None,
        description='Whether the file is binary. (not set if false)',
    )


class GitPersonInfo(BaseModelGerrit):
    """
    The GitPersonInfo entity contains information about the author/committer of a commit.

    https://gerrit-review.googlesource.com/Documentation/rest-api-changes.html#git-person-info

    Example:
        https://gerrit-review.googlesource.com/Documentation/rest-api-projects.html#get-tag (`tagger` field)
        {
            "name": "David Pursehouse",
            "email": "david.pursehouse@sonymobile.com",
            "date": "2014-10-06 07:35:03.000000000",
            "tz": 540
        }
    """

    name: str = Field(
        description='The name of the author/committer.',
    )
    email: str = Field(
        description='The email address of the author/committer.',
    )
    date: str = Field(
        # TODO(aj): Convert this to a datetime field?
        # https://gerrit-review.googlesource.com/Documentation/rest-api.html#timestamp
        description='The timestamp of when this identity was constructed. Timestamps are given in UTC and have the format "yyyy-mm-dd hh:mm:ss.fffffffff" where "fffffffff" represents nanoseconds.',
    )
    tz: int = Field(
        description='The timezone offset from UTC of when this identity was constructed.',
    )


class WebLinkInfo(BaseModelGerrit):
    """
    The WebLinkInfo entity describes a link to an external site.

    https://gerrit-review.googlesource.com/Documentation/rest-api-changes.html#web-link-info

    Example:
        https://gerrit-review.googlesource.com/Documentation/rest-api-changes.html#get-edit-meta-data
        {
            "name": "side-by-side preview diff",
            "image_url": "plugins/xdocs/static/sideBySideDiffPreview.png",
            "url": "#/x/xdocs/c/42/1..0/README.md",
        }
    """

    # TODO(aj): How about the `target` field that appears in the examples?

    name: str = Field(
        description='The text to be linkified.',
    )
    tooltip: str | None = Field(
        default=None,
        description='Tooltip to show when hovering over the link. Using "Open in $NAME_OF_EXTERNAL_TOOL" is a good option here.',
    )
    url: str = Field(
        description='The link URL.',
    )
    image_url: str | None = Field(
        default=None,
        description='URL to the icon of the link.',
    )


class DiffWebLinkInfo(WebLinkInfo):  # note the parent class
    """
    The DiffWebLinkInfo entity extends WebLinkInfo and describes a link on a diff screen to an external site.

    https://gerrit-review.googlesource.com/Documentation/rest-api-changes.html#diff-web-link-info

    Example:
        https://gerrit-review.googlesource.com/Documentation/rest-api-changes.html#get-edit-meta-data
        {
            "show_on_side_by_side_diff_view": true,
            "name": "side-by-side preview diff",
            "image_url": "plugins/xdocs/static/sideBySideDiffPreview.png",
            "url": "#/x/xdocs/c/42/1..0/README.md",
            "target": "_self"
        }
    """

    # TODO(aj): How about the `target` field that appears in the examples?

    show_on_side_by_side_diff_view: bool = Field(
        description='Whether the web link should be shown on the side-by-side diff screen.'
    )
    show_on_unified_diff_view: bool = Field(
        description='Whether the web link should be shown on the unified diff screen.'
    )
