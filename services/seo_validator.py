from models.report import CheckStatus, PageDetails, SeoChecks

# TODO: we can set this values as per different SEO guidelines in future
# https://moz.com/
# https://ahrefs.com/seo/

TITLE_MIN_LENGTH = 10
TITLE_MAX_LENGTH = 60
META_MIN_LENGTH = 50
META_MAX_LENGTH = 160
CONTENT_PASS_MIN_WORDS = 300
CONTENT_WARNING_MIN_WORDS = 100


def validate_seo(page_details: PageDetails) -> SeoChecks:
    return SeoChecks(
        title_check=_title_check(page_details.title),
        meta_description_check=_meta_description_check(page_details.meta_description),
        h1_check=_h1_check(page_details.h1_tags),
        alt_text_check=_alt_text_check(page_details.image_count, page_details.missing_alt_count),
        content_length_check=_content_length_check(page_details.word_count),
    )


def _title_check(title: str) -> CheckStatus:
    if not title.strip():
        return "FAIL"

    length = len(title.strip())
    if TITLE_MIN_LENGTH <= length <= TITLE_MAX_LENGTH:
        return "PASS"

    return "WARNING"


def _meta_description_check(meta_description: str) -> CheckStatus:
    if not meta_description.strip():
        return "FAIL"

    length = len(meta_description.strip())
    if META_MIN_LENGTH <= length <= META_MAX_LENGTH:
        return "PASS"

    return "WARNING"


def _h1_check(h1_tags: list[str]) -> CheckStatus:
    if not h1_tags:
        return "FAIL"

    if len(h1_tags) == 1:
        return "PASS"

    return "WARNING"


def _alt_text_check(image_count: int, missing_alt_count: int) -> CheckStatus:
    if image_count == 0:
        return "PASS"

    if missing_alt_count == 0:
        return "PASS"

    if missing_alt_count == image_count:
        return "FAIL"

    return "WARNING"


def _content_length_check(word_count: int) -> CheckStatus:
    if word_count >= CONTENT_PASS_MIN_WORDS:
        return "PASS"

    if word_count >= CONTENT_WARNING_MIN_WORDS:
        return "WARNING"

    return "FAIL"
