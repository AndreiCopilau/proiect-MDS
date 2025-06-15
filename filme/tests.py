from django.test import TestCase, Client
from django.urls import reverse
from .models import UserCustom, Film, Favorite, ViewHistory
from django.utils import timezone

        
class FavoriteTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = UserCustom.objects.create_user(username='user1', password='pass')
        self.client.login(username='user1', password='pass')
        self.film = Film.objects.create(id_tmdb=9999, titlu="Test Movie")

    def test_adaugare_favorit(self):
        response = self.client.get(reverse('adauga_favorit', args=[9999]))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Favorite.objects.filter(user=self.user, film=self.film).exists())

    def test_favorit_nu_se_adauga_de_doua_ori(self):
        Favorite.objects.create(user=self.user, film=self.film)
        response = self.client.get(reverse('adauga_favorit', args=[9999]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Favorite.objects.filter(user=self.user, film=self.film).count(), 1)


class IstoricVizionariTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = UserCustom.objects.create_user(username='user2', password='pass')
        self.client.login(username='user2', password='pass')
        self.film = Film.objects.create(id_tmdb=5555, titlu="Vizionat")

        ViewHistory.objects.create(user=self.user, film=self.film, viewed_at=timezone.now())

    def test_istoric_afiseaza(self):
        response = self.client.get(reverse('istoric_vizionari'))
        self.assertContains(response, "Vizionat")

    def test_istoric_vid(self):
        ViewHistory.objects.all().delete()
        response = self.client.get(reverse('istoric_vizionari'))
        self.assertContains(response, "Nu ai vizionat încă niciun film.", status_code=200)


class UtilizatorTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.utilizator = UserCustom.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com',
            email_confirmat=True
        )

    def test_inregistrare_valida(self):
        response = self.client.post(reverse('register'), {
            'username': 'nou_user',
            'email': 'nou@email.com',
            'telefon': '0712345678',
            'data_nasterii': '2000-01-01',
            'gen': 'M',
            'password1': 'Testparola123!',
            'password2': 'Testparola123!',
        })
        self.assertEqual(response.status_code, 302)  # redirect
        self.assertTrue(UserCustom.objects.filter(username='nou_user').exists())

    def test_inregistrare_username_interzis(self):
        response = self.client.post(reverse('register'), {
            'username': 'admin',
            'email': 'admin@email.com',
            'telefon': '0700000000',
            'data_nasterii': '1990-01-01',
            'gen': 'M',
            'password1': 'Testparola123!',
            'password2': 'Testparola123!',
        }, follow=True)
        self.assertContains(response, "Nu poti folosi acest username.", status_code=200)

    def test_login_fara_confirmare_email(self):
        user = UserCustom.objects.create_user(
            username='noemail',
            password='parolatest',
            email='noemail@test.com',
            email_confirmat=False
        )
        response = self.client.post(reverse('login'), {
            'username': 'noemail',
            'password': 'parolatest'
        }, follow=True)
        self.assertContains(response, "Adresa de email nu este confirmata", status_code=200)

    def test_login_cu_confirmare_email(self):
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertRedirects(response, reverse('home'))

    def test_login_esuat(self):
        response = self.client.post(reverse('login'), {
            'username': 'inexistent',
            'password': 'gresita'
        })
        self.assertContains(response, "Autentificare esuata", status_code=200)


class ConfirmareEmailTest(TestCase):
    def test_confirmare_valida(self):
        user = UserCustom.objects.create_user(
            username='cuconfirmare',
            password='12345',
            cod='abc123',
            email_confirmat=False
        )
        response = self.client.get(reverse('confirma_mail', args=['abc123']))
        user.refresh_from_db()
        self.assertTrue(user.email_confirmat)
        self.assertIsNone(user.cod)
        self.assertContains(response, "E-mailul a fost confirmat cu succes")

    def test_confirmare_cod_invalid(self):
        response = self.client.get(reverse('confirma_mail', args=['cod_inexistent']), follow=True)
        self.assertContains(response, "Codul de confirmare este invalid sau a expirat.", status_code=200)
