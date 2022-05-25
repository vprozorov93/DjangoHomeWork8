import pytest
from students.models import Course, Student


@pytest.mark.django_db
def test_retrieve_course(client, course_factory):
    course_list = course_factory(_quantity=1)
    url = f'/api/v1/courses/{course_list[0].id}/'

    response = client.get(path=url)

    assert response.status_code == 200
    assert response.json()['id'] == course_list[0].id


@pytest.mark.django_db
def test_list_courses(client, student_factory, course_factory):
    course_list = course_factory(_quantity=2)
    students_list_1 = student_factory(_quantity=10)
    students_list_2 = student_factory(_quantity=10)
    for student in students_list_1:
        course_list[0].students.add(student.id)
    for student in students_list_2:
        course_list[1].students.add(student.id)

    response = client.get(path='/api/v1/courses/')

    assert response.status_code == 200
    data = response.json()
    assert data[0]['id'] == course_list[0].id and data[0]['students'] == [student.id for student in students_list_1]
    assert data[1]['id'] == course_list[1].id and data[1]['students'] == [student.id for student in students_list_2]


@pytest.mark.django_db
def test_list_course_filter_id_and_name(client, course_factory):
    course_list = course_factory(_quantity=2)
    url1 = f'/api/v1/courses/?id={course_list[1].id}'
    url2 = f'/api/v1/courses/?name={course_list[0].name}'

    response1 = client.get(path=url1)
    response2 = client.get(path=url2)
    assert response1.status_code == 200
    assert len(response1.json()) == 1
    assert response1.json()[0]['id'] == course_list[1].id
    assert response2.status_code == 200
    assert len(response2.json()) == 1
    assert response2.json()[0]['name'] == course_list[0].name


@pytest.mark.django_db
def test_post_course(client, student_factory):
    students_list = student_factory(_quantity=10)
    course_count = Course.objects.count()
    response1 = client.post(path='/api/v1/courses/',
                            data={
                                'name': 'Курс Нетология',
                                'students': [student.id for student in students_list]
                            },
                            format='json')

    assert response1.status_code == 201
    assert response1.json()['name'] == 'Курс Нетология'
    assert Student.objects.count() == course_count+1


@pytest.mark.django_db
def test_update_course(client, course_factory):
    course_list = course_factory(_quantity=1)

    url = f'/api/v1/courses/{course_list[0].id}/'
    response2 = client.patch(path=url, data={'name': 'COURSE'}, format='json')

    assert response2.status_code in [200, 204]
    assert Course.objects.filter(id=course_list[0].id)[0].name == 'COURSE'


@pytest.mark.django_db
def test_delete_course(client, course_factory, student_factory):
    course_list = course_factory(_quantity=1)
    url = f'/api/v1/courses/{course_list[0].id}/'

    response = client.delete(path=url)

    assert response.status_code in [200, 204]
    assert Course.objects.filter(id=course_list[0].id).count() == 0
