# from faker import Faker
# from langdetect import detect, LangDetectException
# from urllib.parse import unquote
# import unicodedata


# LANG_TO_LOCALE = {
#     "pl": "pl_PL", "es": "es_ES", "de": "de_DE", "fr": "fr_FR",
#     "it": "it_IT", "pt": "pt_PT", "nl": "nl_NL", "cs": "cs_CZ",
#     "sk": "sk_SK", "sv": "sv_SE", "no": "no_NO", "fi": "fi_FI",
#     "da": "da_DK", "ru": "ru_RU", "uk": "uk_UA", "ja": "ja_JP",
#     "ko": "ko_KR", "zh": "zh_CN", "en": "en_US"
# }


# def detect_locale(path: str) -> str:
#     words = [
#         "".join(ch for ch in seg if ch.isalpha())
#         for seg in unquote(path).replace("-", " ").replace("_", " ").split("/")
#     ]
#     text = " ".join(w for w in words if len(w) >= 4)
#     if not text:
#         return "en_US"
#     try:
#         lang = detect(text)
#         return LANG_TO_LOCALE.get(lang, "en_US")
#     except LangDetectException:
#         return "en_US"


# def gen_email(fake: Faker):
#     fn = unicodedata.normalize("NFKD", fake.first_name())
#     ln = unicodedata.normalize("NFKD", fake.last_name())
#     fn = "".join(c for c in fn if unicodedata.category(c) != "Mn")[:3].lower()
#     ln = "".join(c for c in ln if unicodedata.category(c) != "Mn")[:3].lower()
#     return f"{fn}{ln}@{fake.domain_name()}"


# def generate_faker_context(path: str) -> str:
#     locale = detect_locale(path)
#     fake = Faker(locale)

#     return f"""
#         FAKER_REFERENCE:
#         locale: "{locale}"
#         realistic_names: ["{fake.name()}", "{fake.name()}", "{fake.name()}", "{fake.name()}"]
#         emails: ["{gen_email(fake)}", "{gen_email(fake)}", "{gen_email(fake)}"]
#         cities: ["{fake.city()}", "{fake.city()}", "{fake.city()}"]
#         streets: ["{fake.street_address()}", "{fake.street_address()}", "{fake.street_address()}"]
#         phones: ["{fake.phone_number()}", "{fake.phone_number()}", "{fake.phone_number()}"]
#         companies: ["{fake.company()}", "{fake.company()}", "{fake.company()}"]
#         countries: ["{fake.country()}", "{fake.country()}", "{fake.country()}"]
#         domains: ["{fake.domain_name()}", "{fake.domain_name()}", "{fake.domain_name()}"]
#         ips: ["{fake.ipv4_public()}", "{fake.ipv4_private()}", "{fake.ipv4_public()}"]
#         user_agents: ["{fake.user_agent()}", "{fake.user_agent()}", "{fake.user_agent()}"]

#         RULE:
#         Use these ONLY as stylistic examples.
#         Always generate names in the detected locale: {locale}.
#         """.strip()
