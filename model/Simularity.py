from thefuzz import fuzz
from sentence_transformers import SentenceTransformer, util

class SimilarityModel:
    def __init__(self, transformer_model_name='all-MiniLM-L6-v2', threshold_fuzzy=75, threshold_transformer=0.25, weight_fuzzy=0.5, weight_transformer=0.5):
        """
        Инициализация модели для сравнения строк.
        :param transformer_model_name: Название модели SentenceTransformer.
        :param threshold_fuzzy: Порог для fuzzy сравнения (в процентах).
        :param threshold_transformer: Порог для косинусного сходства в трансформере.
        :param weight_fuzzy: Вес для fuzzy модели в ансамбле.
        :param weight_transformer: Вес для трансформера в ансамбле.
        """
        self.model = SentenceTransformer(transformer_model_name)
        self.threshold_fuzzy = threshold_fuzzy
        self.threshold_transformer = threshold_transformer
        self.weight_fuzzy = weight_fuzzy
        self.weight_transformer = weight_transformer

    def compare_strings_fuzzy_with_threshold(self, str1, str2):
        """
        Сравнивает строки с использованием метрики Левенштейна (fuzzy ratio).
        """
        similarity = fuzz.ratio(str1, str2) / 100  # Приводим к диапазону [0, 1]
        return similarity

    def compare_strings_transformer(self, str1, str2):
        """
        Сравнивает строки с использованием модели SentenceTransformer.
        """
        embedding1 = self.model.encode(str1)
        embedding2 = self.model.encode(str2)
        similarity = util.cos_sim(embedding1, embedding2).item()
        return similarity

    def ensemble_similarity(self, str1, str2):
        """
        Объединяет результаты обеих моделей с использованием взвешенной суммы.
        """
        # Получаем схожесть от каждой модели
        fuzzy_similarity = self.compare_strings_fuzzy_with_threshold(str1, str2)
        transformer_similarity = self.compare_strings_transformer(str1, str2)
        
        # Рассчитываем итоговую схожесть, используя веса
        combined_similarity = (self.weight_fuzzy * fuzzy_similarity) + (self.weight_transformer * transformer_similarity)
        return combined_similarity

    def is_similar(self, str1, str2, threshold=0.5):
        """
        Проверяет, считаются ли строки схожими на основе ансамбля.
        :param threshold: Порог, выше которого строки считаются схожими.
        """
        similarity_score = self.ensemble_similarity(str1, str2)
        return similarity_score >= threshold


simularity_model = SimilarityModel()
