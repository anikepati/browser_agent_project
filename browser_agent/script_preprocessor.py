import json
from logging_setup import setup_logging
from config import AppConfig

class ScriptPreprocessor:
    @staticmethod
    def preprocess(script, task_item):
        logger = setup_logging()
        if not isinstance(task_item, dict):
            raise ValueError("task_item must be a dictionary")
        try:
            updated_script = json.loads(json.dumps(script))  # Deep copy
            # Inject current date for form-filling
            task_item['current_date'] = AppConfig.CURRENT_DATE
            for action in updated_script['actions']:
                params = action.get('parameters', {})
                if not isinstance(params, dict):
                    continue
                for key, value in params.items():
                    if isinstance(value, str) and value.startswith('{{') and value.endswith('}}'):
                        param_path = value[2:-2].split('.')
                        current = task_item
                        for part in param_path:
                            current = current.get(part) if isinstance(current, dict) else value  # Safer fallback
                        action['parameters'][key] = current
            logger.info("Preprocessed script with task_item and current date.")
            return updated_script
        except json.JSONDecodeError as e:
            logger.error(f"JSON error in preprocessing: {str(e)}")
            raise
