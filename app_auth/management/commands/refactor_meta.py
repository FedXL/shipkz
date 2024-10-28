from django.core.management.base import BaseCommand
from app_auth.models import Profile, CustomUser
from legacy.models import WebUsersMeta, WebUsers


class Command(BaseCommand):
    help = 'create from meta users'

    def handle(self, *args, **kwargs):
        web_users = WebUsers.objects.all()
        counter = 0
        lent = len(web_users)
        for web_user in web_users:
            print(counter,"from",lent)
            web_user_infos = WebUsersMeta.objects.filter(web_user=web_user)
            counter +=1
            if not web_user_infos:
                continue
            custom_user = CustomUser.objects.filter(username=web_user.web_username).first()
            if custom_user:
                continue
            username =WebUsersMeta.objects.filter(web_user=web_user,field='username').first()
            if username:
                username = username.value
            email = WebUsersMeta.objects.filter(web_user=web_user,field='user_email').first()
            if email:
                email = email.value
            user_registration_date = WebUsersMeta.objects.filter(web_user=web_user,field='user_registered').first()
            if user_registration_date:
                user_registration_date = user_registration_date.value
            first_name = WebUsersMeta.objects.filter(web_user=web_user,field='first_name').first()
            if first_name:
                first_name = first_name.value

            last_name = WebUsersMeta.objects.filter(web_user=web_user,field='last_name').first()
            if last_name:
                last_name = last_name.value
            description = WebUsersMeta.objects.filter(web_user=web_user,field='description').first()
            if description:
                description = description.value
            phone_number = WebUsersMeta.objects.filter(web_user=web_user,field='phone_number').first()
            if phone_number:
                phone_number=phone_number.value

            cdek_address = WebUsersMeta.objects.filter(web_user=web_user,field='cdek_adress').first()

            if cdek_address:
                cdek_address = cdek_address.value
            telegram_id = WebUsersMeta.objects.filter(web_user=web_user,field='telegram').first()
            if telegram_id:
                telegram_id = telegram_id.value

            if username != web_user.web_username:
                print('ERROR',web_user.user_id)
                continue

            if not telegram_id or telegram_id=="":
                telegram_id = None

            if isinstance(telegram_id,str):
                telegram_id = None

            custom_user,create = CustomUser.objects.get_or_create(username=web_user.web_username, email=email)
            profile,create = Profile.objects.get_or_create(user=custom_user,
                                                    first_name=first_name,
                                                    last_name=last_name,
                                                    email=email,
                                                    phone=phone_number,
                                                    cdek_address=cdek_address,
                                                    telegram_id=telegram_id,
                                                    web_user=web_user
                                                    )

