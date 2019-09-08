import app
from routes.index import profile
import cProfile
from pstats import Stats


def profile_request(path, cookie, f):
    a = app.configured_app()
    pr = cProfile.Profile()
    headers = {'Cookie': cookie}

    with a.test_request_context(path, headers=headers):
        pr.enable()

        # r = f()
        # assert type(r) == str, r
        f()

        pr.disable()

    pr.create_stats()
    s = Stats(pr).sort_stats('cumulative')
    s.dump_stats('profile.pstat')

    s.print_stats('.*new_web.*')
    # s.print_callers()


if __name__ == '__main__':
    path = '/profile'
    cookie = 'session=eyJfcGVybWFuZW50Ijp0cnVlLCJ1c2VyX2lkIjoyfQ.EEfTcw.Nj_VNc_fEZLb8MsMmfuIjOxeWSk'
    profile_request(path, cookie, profile)
