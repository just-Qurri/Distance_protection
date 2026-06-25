"""
Менеджер сохранения и загрузки конфигурации (оптимизирован)
"""

import json
import os
from datetime import datetime
from typing import Any, Dict, Optional


class ConfigManager:
    """Менеджер конфигурации"""

    def __init__(self, app_name: str = "REL670_Visualizer"):
        self.app_name = app_name
        self.config_dir = os.path.join(os.path.expanduser("~"), f".{app_name}")
        self._ensure_config_dir()

    def _ensure_config_dir(self) -> None:
        """Создать директорию для конфигурации"""
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)

    def get_config_path(self, filename: str = "config.json") -> str:
        """Получить полный путь к файлу конфигурации"""
        return os.path.join(self.config_dir, filename)

    def save_config(self, config: Dict[str, Any], filename: str = "config.json") -> bool:
        """Сохранить конфигурацию в файл"""
        try:
            config['_metadata'] = {
                'saved_at': datetime.now().isoformat(),
                'app_name': self.app_name,
                'version': '1.0'
            }
            with open(self.get_config_path(filename), 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2, default=str)
            return True
        except Exception as e:
            print(f"Ошибка сохранения конфигурации: {e}")
            return False

    def load_config(self, filename: str = "config.json") -> Optional[Dict[str, Any]]:
        """Загрузить конфигурацию из файла"""
        try:
            filepath = self.get_config_path(filename)
            if not os.path.exists(filepath):
                return None
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Ошибка загрузки конфигурации: {e}")
            return None

    def apply_config(self, config: Dict[str, Any], visualizer) -> bool:
        """Применить конфигурацию напрямую к визуализатору"""
        try:
            # Сохраняем во временный файл и загружаем
            import tempfile
            import os as os_module

            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(config, f, indent=2)
                temp_file = f.name

            try:
                success = visualizer.load_configuration(temp_file)
                return success
            finally:
                if os_module.path.exists(temp_file):
                    os_module.remove(temp_file)
        except Exception as e:
            print(f"Ошибка применения конфигурации: {e}")
            return False

    def list_configs(self) -> list:
        """Получить список доступных конфигураций"""
        return sorted([f for f in os.listdir(self.config_dir) if f.endswith('.json')])

    def delete_config(self, filename: str) -> bool:
        """Удалить файл конфигурации"""
        try:
            filepath = self.get_config_path(filename)
            if os.path.exists(filepath):
                os.remove(filepath)
                return True
            return False
        except Exception as e:
            print(f"Ошибка удаления конфигурации: {e}")
            return False

    def export_config(self, config: Dict[str, Any], filepath: str) -> bool:
        """Экспортировать конфигурацию в указанный файл"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2, default=str)
            return True
        except Exception as e:
            print(f"Ошибка экспорта: {e}")
            return False

    def import_config(self, filepath: str) -> Optional[Dict[str, Any]]:
        """Импортировать конфигурацию из файла"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Ошибка импорта: {e}")
            return None
