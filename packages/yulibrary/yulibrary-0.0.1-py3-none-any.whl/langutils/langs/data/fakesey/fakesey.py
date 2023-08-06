import random

from faker import Faker


object_methods = [
    "currency",
    "simple_profile",
    "pylist",
    "pyset",
    "pytuple",
    "pystruct",
]


number_methods = [
    "random_int",
    "random_digit",
    "pyfloat",
    "pybool",
    "pydecimal",
    "pyint",
]


date_methods_onlydates = [
    # 'unix_time',
    "date_time",
    "iso8601",
    "date",
    # 'time',
    "date_time_this_century",
    "date_time_this_decade",
    "date_time_this_year",
    "date_time_this_month",
    "date_this_century",
    "date_this_decade",
    "date_this_year",
    "date_this_month",
]


date_methods = [
    "date_of_birth",
    # 'century',
    "year",
    "month",
    "month_name",
    "day_of_week",
    "day_of_month",
    # 'timezone',
    # 'am_pm',
    "unix_time",
    "date_time",
    "iso8601",
    "date",
    "time",
    "date_time_this_century",
    "date_time_this_decade",
    "date_time_this_year",
    "date_time_this_month",
    "date_this_century",
    "date_this_decade",
    "date_this_year",
    "date_this_month",
]


list_methods = [
    "paragraphs",
    "words",
    "sentences",
    "texts",
]


string_methods = [
    "name",
    "password",
    "phone_number",
    "first_name",
    "last_name",
    "name_male",
    "name_female",
    # https://faker.readthedocs.io/en/master/providers/faker.providers.color.html
    "color",
    # https://faker.readthedocs.io/en/master/providers/faker.providers.lorem.html
    "paragraph",
    # 'paragraphs',
    "word",
    # 'words',
    "sentence",
    # 'sentences',
    "text",
    # 'texts',
    "job",
    # https://faker.readthedocs.io/en/master/providers/faker.providers.company.html
    "company",
    "address",
    "currency_name",
    "currency_code",
    "email",
    "safe_email",
    "free_email",
    "company_email",
    "hostname",
    "domain_name",
    "domain_word",
    "tld",
    "ipv4",
    "ipv6",
    "mac_address",
    "slug",
    "image_url",
    "pystr",
    "ssn",
    "md5",
    "sha1",
    "sha256",
    "uuid4",
    # https://faker.readthedocs.io/en/master/providers/faker.providers.user_agent.html
    "chrome",
    "firefox",
    "opera",
    "safari",
    "internet_explorer",
    "user_agent",
]


class Fakesey:
    def __init__(self, *args, **kwargs):
        self.config = {}
        if "locale" in kwargs.keys():
            pilih_locale = kwargs["locale"]
            if "," in pilih_locale:
                pilih_locale = pilih_locale.split(",")
            print("pilih_locale:", pilih_locale)
            self.faker = Faker(pilih_locale)
        else:
            self.faker = Faker()

    def gen(self, methodname):
        return getattr(self.faker, methodname)()

    def generate(self, methodname, *args, **kwargs):
        """
        kembali = getattr(faker_instance, f'generate') ('random_int', min, max)
        kembali = getattr(faker_instance, f'generate') ('random_int', min)
        """
        try:
            cek_bcrypt = getattr(self.faker, methodname)(*args, **kwargs)
            return cek_bcrypt
        except Exception as e:
            import traceback

            print("gagal fakesey/generate:", e)
            print(f"""
			methodname: {methodname}
			args: {args}
			kwargs: {kwargs}
			""")
            print(traceback.format_exc())
            input("Press any key... ")

    def _string(self, number=None):
        """
        hati2 jangan sampai
        random.choice(string_methods)
        mengembalikan list
        """
        if number:
            return self.faker.text(number)
        return getattr(self.faker, random.choice(string_methods))()

    def _text(self, number=500):
        if number:
            return self.faker.text(number)
        return getattr(self.faker, random.choice(string_methods))()

    def _date(self):
        # return getattr(self.faker, random.choice(date_methods)) ()
        return getattr(self.faker, random.choice(date_methods_onlydates))()

    def _number(self):
        return getattr(self.faker, random.choice(number_methods))()

    def _object(self):
        return getattr(self.faker, random.choice(object_methods))()

    def _url(self):
        return self.faker.url()


palsu = Fakesey()
# if 'locale' in configuration:
#   print('gunakan locale:', configuration['locale'])
#   palsu = Fakesey(locale=configuration['locale'])
