from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpResponse
from django.http import JsonResponse
from django.shortcuts import redirect
from django.template import loader

from .auth_backend import AuthBackend
from .forms import *
from .models import Game, STATUS_ACTIVE, STATUS_OVER, STATUS_INACTIVE, STATUS_TIE, BOARD_SIZE


@login_required(login_url='/signin')
def home(request):
    """ Home View """
    return redirect('game')


@login_required(login_url='/signin')
def make_move(request):
    """ Make Move View """
    data = {'success': True, 'message': ''}
    row = int(request.POST['row'])
    col = int(request.POST['col'])

    game_id = request.session['game_id']
    game = Game.objects.filter(id=game_id).first()

    # Should not happen, just in case of bug on the client side
    if not game.is_legal_move(row, col):
        data['success'] = False
        data['message'] = 'Got invalid row or column'
        return JsonResponse(status=400, data=data)

    if game.status in (STATUS_OVER, STATUS_TIE):
        data['success'] = False
        data['message'] = 'Game is already over'
        return JsonResponse(status=400, data=data)

    if not game.is_free_cell(row, col):
        data['success'] = False
        data['message'] = 'The space is occupied. '
        return JsonResponse(status=400, data=data)

    game.set_move(row, col)

    if game.status == STATUS_ACTIVE and game.current_player is None:
        game.computer_move()

    game_data = game.get_game_data()

    return JsonResponse(game_data)


@login_required(login_url='/signin')
def game(request):
    """ Game View """
    if request.method == 'GET':
        current_game = Game.objects.filter(
            Q(status=STATUS_ACTIVE),
            Q(player_x=request.user) | Q(player_o=request.user)).first()

        if not current_game:
            # Start a new game
            current_game = Game()
            current_game.init_game(player_one=request.user)

        if current_game.current_player is None:
            current_game.computer_move()

        request.session['game_id'] = current_game.id
        request.session['board'] = current_game.board
        template = loader.get_template('current_game.html')
        context = {
            'board': current_game.board,
            'board_size_range': range(BOARD_SIZE),
            'board_size': BOARD_SIZE,
            'player': current_game.get_player_name(),
            'player_designation': current_game.get_current_player_designation()
        }

        return HttpResponse(template.render(context, request))


def signin(request):
    """ Signin View """
    # Signin button was clicked
    if request.method == 'POST':
        email = request.POST['email']
        form = SigninForm(request.POST)
        user = AuthBackend().authenticate(email=email)
        if user is not None:
            login(request, user)
            return redirect('game')  # Redirect to game
        else:
            # User tried to signin with an non existing user
            form.add_error('email', "Cannot sign in. Email not found.")
            template = loader.get_template('signin.html')
            context = {
                'form': form,
            }
            return HttpResponse(template.render(context, request))

    # Entering the signin page
    if request.method == 'GET':
        template = loader.get_template('signin.html')
        context = {
            'form': SigninForm()
        }
        return HttpResponse(template.render(context, request))


def signout(request):
    """ Signout View"""
    logout(request)
    return redirect('home')


def signup(request):
    """ Signup View"""
    if request.method == 'POST':
        email = request.POST['email']
        name = request.POST['name']
        form = SignupForm(request.POST)

        try:
            User.objects.get(email=email)
            form.add_error('email', "Cannot sign up. Email already exists.")
            template = loader.get_template('signup.html')
            context = {
                'form': form,
            }
            return HttpResponse(template.render(context, request))

        except User.DoesNotExist:
            # Create new user
            user = User(first_name=name, email=email, username=email)
            user.save()
            # Sign in the new user
            login(request, user)
            return redirect('game')

    if request.method == 'GET':
        template = loader.get_template('signup.html')
        context = {
            'form': SignupForm()
        }
        return HttpResponse(template.render(context, request))


def new_game(request):
    """ New Game View"""
    current_game = Game.objects.filter(
        Q(status=STATUS_ACTIVE),
        Q(player_x=request.user) | Q(player_o=request.user)).first()

    if current_game:
        # Game stopped prematurely, set it to inactive
        current_game.set_status(STATUS_INACTIVE)

    return redirect('game')
