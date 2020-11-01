import requests
import sys
from config import auth_params, base_url, board_id

def read():
  column_data = requests.get(base_url.format('boards') + '/' + board_id + '/lists', params=auth_params).json()       
  for column in column_data:      
    print(column['name'])         
    task_data = requests.get(base_url.format('lists') + '/' + column['id'] + '/cards', params=auth_params).json()      
    if not task_data:      
      print('\t' + 'Нет задач!')      
      continue      
    for task in task_data:      
      print('\t' + task['name'])

def createTask(name, column_name):          
  column_data = requests.get(base_url.format('boards') + '/' + board_id + '/lists', params=auth_params).json()         
  for column in column_data:      
    if column['name'].split('(')[0].rstrip() == column_name:        
      requests.post(base_url.format('cards'), data={'name': name, 'idList': column['id'], **auth_params})      
      return True
  print('Листа с названием {} не существует!'.format(column_name))
  return False

def getLongBoardId(board_id):
  board_data = requests.get(base_url.format('boards') + '/' + board_id, params=auth_params).json()
  return board_data['id']

def columnCreate(new_column_name):
  column_data = requests.get(base_url.format('boards') + '/' + board_id + '/lists', params=auth_params).json()
  for column in column_data:
    if (column['name'].split('(')[0].rstrip() == new_column_name):
      print('Лист с названием {} уже существует! Придумайте другое название..\n'.format(new_column_name))
      return False
  longBoardId = getLongBoardId(board_id)
  requests.post(base_url.format('lists'), data={'idBoard': longBoardId, 'name': new_column_name, **auth_params})
  print('Лист {} успешно создан!\n'.format(new_column_name))

def archiveList(column_name):
  column_data = requests.get(base_url.format('boards') + '/' + board_id + '/lists', params=auth_params).json()
  for column in column_data:
    if (column['name'].split('(')[0].rstrip() == column_name):
      requests.put(base_url.format('lists/') + column['id'] + '/closed', data={'value': 'true', **auth_params})
      print('Лист {} успешно отправлен в архив!'.format(column_name))
      return True
  print('Листа с названием {} не существует!'.format(column_name))
  return False

def updateColumnName():
  column_data = requests.get(base_url.format('boards') + '/' + board_id + '/lists', params=auth_params).json()
  for column in column_data:
    column_tasks = requests.get(base_url.format('lists') + '/' + column['id'] + '/cards', params=auth_params).json()
    newColumnName = '{} ({})'.format(column['name'].split('(')[0].rstrip(), len(column_tasks))
    requests.put(base_url.format('lists') + '/' + column['id'], data = {'name' : newColumnName, **auth_params})

def getAvailableLists():
  column_data = requests.get(base_url.format('boards') + '/' + board_id + '/lists', params=auth_params).json()
  allLists = []
  for column in column_data:
    allLists.append(column)
  return allLists

def getAvailableTasks():
  allTasks = []
  column_data = requests.get(base_url.format('boards') + '/' + board_id + '/lists', params=auth_params).json()       
  for column in column_data:               
    task_data = requests.get(base_url.format('lists') + '/' + column['id'] + '/cards', params=auth_params).json()
    for task in task_data:
      allTasks.append(task)
  return allTasks

if __name__ == "__main__":
  try:
    response = requests.get(base_url.format('boards') + '/' + board_id, params=auth_params)
    response.raise_for_status()
  except requests.exceptions.HTTPError as e:
    print('Не удалось получить данные от {}\n{}\nЗавершение программы..'.format(response.url,e))
    sys.exit()
  while(True):
    print('\nCLI для работы с доской {} на trello.com'.format(response.json()['name']))
    print('\nМеню:')
    print('\t 1 - Показать доску')
    print('\t 2 - Добавить лист')
    print('\t 3 - Архивировать лист')
    print('\t 4 - Добавить задачу')
    print('\t 5 - Переместить задачу')
    print('\t 6 - Выход\n')
    choose = input('Делайте Ваш выбор: -> ')
    if (choose == '1'):
      updateColumnName()
      read()

    elif (choose == '2'):
      new_column_name = input('Введите название нового листа: -> ')
      columnCreate(new_column_name)
      updateColumnName()

    elif (choose == '3'):
      availableLists = getAvailableLists()
      i = 0
      print('\nДоступные листы:')
      for availableList in availableLists:
        i += 1
        print('\t{} - {}'.format(i, availableList['name'].split('(')[0].rstrip()))
      try:
        column_name_archive = int(input('Введите номер листа, который необходимо отправить в архив: -> '))
        if (column_name_archive < 1):
          print('Номер листа должен быть больше 0')
          continue
        else:
          archiveList(availableLists[column_name_archive - 1]['name'].split('(')[0].rstrip())
      except ValueError:
        print('\nНе корректный номер листа. Необходимо ввести число')
        continue
      except LookupError:
        print('\nНе корректный номер листа')
        continue

    elif (choose == '4'):
      availableLists = []
      availableLists = getAvailableLists()
      i = 0
      print('\nДоступные листы:')
      for availableList in availableLists:
        i += 1
        print('\t{} - {}'.format(i, availableList['name'].split('(')[0].rstrip()))
      try:
        column_name_add = int(input('Введите номер листа, в который необходимо добавить задачу: -> '))
        if (column_name_add < 1):
          print('Номер листа должен быть больше 0')
          continue
        else:
          availableLists[column_name_add - 1]
      except ValueError:
        print('\nНе корректный номер листа. Необходимо ввести число')
        continue
      except LookupError:
        print('\nНе корректный номер листа')
        continue
      name = input('Введите текст новой задачи: -> ')
      createTask(name, availableLists[column_name_add - 1]['name'].split('(')[0].rstrip())
      updateColumnName()

    elif (choose == '5'):
      i = 0
      print('Доступные задачи для перемещения:\n')
      allTasks = getAvailableTasks()
      dictLists = {}
      allLists = getAvailableLists()
      for availableList in allLists:
        dictLists[availableList['id']] = availableList['name'] 
      for task in allTasks:
        i += 1
        print('\t{} - {} (id - {} в колонке "{}")'.format(i,task['name'],task['id'], dictLists[task['idList']].split('(')[0].rstrip()))
      try:
        task_number = int(input('Введите номер задачи, которую необходимо переместить: -> '))
        if (task_number < 1):
          print('Номер задачи должен быть больше 0')
          continue
        else:
          allTasks[task_number - 1]
      except ValueError:
        print('\nНе корректный номер задачи. Необходимо ввести число')
        continue
      except LookupError:
        print('\nНе корректный номер задачи')
        continue
      task_id = allTasks[task_number - 1]['id']
      print('\nДоступные листы:')
      i = 0
      for availableList in allLists:
        i += 1
        print('\t{} - {}'.format(i, availableList['name'].split('(')[0].rstrip()))
      try:
        column_number = int(input('Введите номер листа, в который необходимо переместить задачу: -> '))
        if (column_number < 1):
          print('Номер листа должен быть больше 0')
          continue
        else:
          allLists[column_number - 1]
      except ValueError:
        print('\nНе корректный номер листа. Необходимо ввести число')
        continue
      except LookupError:
        print('\nНе корректный номер листа')
        continue
      requests.put(base_url.format('cards') + '/' + task_id + '/idList', data={'value': allLists[column_number - 1]['id'], **auth_params})
      updateColumnName()
      
    elif (choose == '6'):
      print('Завершение программы..')
      sys.exit()
