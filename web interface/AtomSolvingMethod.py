from model import model, promt_function
from JSON_Functions import *
from tqdm import tqdm
from pathlib import Path
from Similarity import simularity_model
            
def GetReglamentsForUseCases(UseCaseText, Dir_to_Reglaments):
    """
    Функция проходит по всем файлам в директории с регламентами и проверяет,
    упоминается ли название файла регламента в тексте Use Case.
    
    :param UseCaseText: текст Use Case
    :param Dir_to_Reglaments: путь к директории с регламентами
    :return: список регламентов, упомянутых в Use Case
    """
    mentioned_reglaments = []
    
    for item in Path(Dir_to_Reglaments).rglob('*'):
        if item.is_file():
            # Приведение названия файла к нижнему регистру
            file_name = item.stem.lower()
            for word in UseCaseText.lower().split():
                if simularity_model.is_similar(word, file_name):
                    mentioned_reglaments.append(item.name)
                    break
    return mentioned_reglaments
        
def CaseAndReglament(path_to_UseCaseFile, path_to_Reglament):
    '''
    UseCaseFile - .txt file
    path_to_Reglament - .json file
    '''
    with open(path_to_UseCaseFile, 'r') as file:
        lines = file.readlines()
        UseCaseText = ''.join(lines)
    with open(path_to_Reglament, 'r', encoding='utf-8') as file:
        try:
            loaded_json = json.load(file)  # Чтение и декодирование JSON
            # print(loaded_json)  # Вывод содержимого JSON
        except json.JSONDecodeError as e:
            print(f"Ошибка при чтении JSON: {e}")
    
    model_answers = ""
    ListOfTechnicalRequirements = unwrap_text(loaded_json, get_list_of_technical_requirements(loaded_json), depth=2)
    for punct in tqdm(ListOfTechnicalRequirements):
        promt = promt_function(UseCaseText, punct)
        model_answers += model.generate_text(promt)
    return model_answers

def CaseAndReglaments(path_to_UseCaseFile, Dir_to_Reglament):
    '''
    UseCaseFile - .txt file
    path_to_Reglament - .json file
    '''
    with open(path_to_UseCaseFile, 'r') as file:
        lines = file.readlines()
        UseCaseText = ''.join(lines)
    mentioned_reglaments = GetReglamentsForUseCases(UseCaseText, Dir_to_Reglament)
    if mentioned_reglaments == []:
        return ''
    answer = ''
    if mentioned_reglaments != None:
        for reglament in mentioned_reglaments:
            answer += CaseAndReglament(path_to_UseCaseFile, Dir_to_Reglament + '/' + reglament) + '\n'
    answer = answer.replace('Not related.', '')
    answer = model.summarize(answer)

    return answer
    
    