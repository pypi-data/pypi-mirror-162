from docparser.core.behavior_base import BehaviorBase
from docparser.core.tools import Tools


class TextRepairBehavior(BehaviorBase):

    class_index = 0

    def data_processing(self, ref_data, data: list, error: list, config: dict, logger, additional) -> dict:

        conf = config.get("text_repair")

        if 'file' not in additional or conf is None:
            return additional

        sub_conf = conf.get('subs')

        if sub_conf is None:
            return additional

        sub_conf = [Tools.init_regex(item) for item in sub_conf]
        lines = config.get("text_repair").get("lines")

        if lines:
            if lines and isinstance(lines, list):
                for line in lines:
                    for sub in sub_conf:
                        res = Tools.match_value(line, sub)
                        if res is not None and isinstance(res, dict):
                            for k, v in res.items():
                                data[k] = v
                                if k == conf.get('stop'):
                                    return additional

        return additional

