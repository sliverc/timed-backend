from datetime import date, timedelta

from django.core.urlresolvers import reverse
from rest_framework import status

from timed.projects.factories import TaskFactory
from timed.tracking.factories import ActivityBlockFactory, ActivityFactory


def test_activity_list(auth_client):
    activity = ActivityFactory.create(user=auth_client.user)
    url = reverse('activity-list')

    response = auth_client.get(url)
    assert response.status_code == status.HTTP_200_OK

    json = response.json()
    assert len(json['data']) == 1
    assert json['data'][0]['id'] == str(activity.id)


def test_activity_detail(auth_client):
    activity = ActivityFactory.create(user=auth_client.user)

    url = reverse('activity-detail', args=[
        activity.id
    ])

    response = auth_client.get(url)
    assert response.status_code == status.HTTP_200_OK


def test_activity_create(auth_client):
    """Should create a new activity and automatically set the user."""
    user = auth_client.user
    task = TaskFactory.create()

    data = {
        'data': {
            'type': 'activities',
            'id': None,
            'attributes': {
                'date': '2017-01-01',
                'comment': 'Test activity'
            },
            'relationships': {
                'task': {
                    'data': {
                        'type': 'tasks',
                        'id': task.id
                    }
                }
            }
        }
    }

    url = reverse('activity-list')

    response = auth_client.post(url, data)
    assert response.status_code == status.HTTP_201_CREATED

    json = response.json()
    assert (
        int(json['data']['relationships']['user']['data']['id']) ==
        int(user.id)
    )


def test_activity_update(auth_client):
    activity = ActivityFactory.create(user=auth_client.user)

    data = {
        'data': {
            'type': 'activities',
            'id': activity.id,
            'attributes': {
                'comment': 'Test activity 2'
            }
        }
    }

    url = reverse('activity-detail', args=[
        activity.id
    ])

    response = auth_client.patch(url, data)
    assert response.status_code == status.HTTP_200_OK

    json = response.json()
    assert (
        json['data']['attributes']['comment'] ==
        data['data']['attributes']['comment']
    )


def test_activity_delete(auth_client):
    activity = ActivityFactory.create(user=auth_client.user)

    url = reverse('activity-detail', args=[
        activity.id
    ])

    response = auth_client.delete(url)
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_activity_list_filter_active(auth_client):
    user = auth_client.user
    ActivityFactory.create(user=user)
    activity = ActivityFactory.create(user=user)
    ActivityBlockFactory.create(activity=activity, to_time=None)

    url = reverse('activity-list')

    response = auth_client.get(url, data={'active': 'true'})
    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert len(json['data']) == 1
    assert json['data'][0]['id'] == str(activity.id)


def test_activity_list_filter_day(auth_client):
    user = auth_client.user
    day = date(2016, 2, 2)
    ActivityFactory.create(date=day - timedelta(days=1), user=user)
    activity = ActivityFactory.create(date=day, user=user)

    url = reverse('activity-list')
    response = auth_client.get(url, data={'day': day.strftime('%Y-%m-%d')})
    assert response.status_code == status.HTTP_200_OK

    json = response.json()
    assert len(json['data']) == 1
    assert json['data'][0]['id'] == str(activity.id)


def test_activity_create_no_task(auth_client):
    """Should create a new activity without a task."""
    data = {
        'data': {
            'type': 'activities',
            'id': None,
            'attributes': {
                'date': '2017-01-01',
                'comment': 'Test activity'
            },
            'relationships': {
                'task': {
                    'data': None
                }
            }
        }
    }

    url = reverse('activity-list')
    response = auth_client.post(url, data)
    assert response.status_code == status.HTTP_201_CREATED

    json = response.json()
    assert json['data']['relationships']['task']['data'] is None
