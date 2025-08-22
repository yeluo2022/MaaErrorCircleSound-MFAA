from maa.agent.agent_server import AgentServer
from maa.custom_recognition import CustomRecognition
from maa.context import Context
import re


# 数值比较识别器
@AgentServer.custom_recognition("CompareNumber")
class CompareNumber(CustomRecognition):
    def analyze(
        self,
        context: Context,
        argv: CustomRecognition.AnalyzeArg,
    ) -> CustomRecognition.AnalyzeResult:
        try:
            # 解析参数
            value_threshold = argv.custom_param.get("value_threshold", 100)
            roi = argv.custom_param.get("roi", [0, 0, 0, 0])

            # 使用 OCR 识别数字
            ocr_result = context.run_recognition(
                "OCR",
                argv.image,
                pipeline_override={
                    "OCR": {
                        "roi": roi,
                        "expected": r"\d+",  # 匹配数字
                        "order_by": "Score",
                        "index": 0,
                    }
                },
            )

            if not ocr_result or not ocr_result.text:
                # OCR 识别失败
                return None

            # 提取数字
            numbers = re.findall(r"\d+", ocr_result.text)
            if not numbers:
                # 未找到数字
                return None

            # 取第一个数字进行比较
            value = int(numbers[0])

            # 比较数值与阈值
            if value > value_threshold:
                # 数值大于阈值，识别成功
                return CustomRecognition.AnalyzeResult(
                    box=ocr_result.box,  # 返回 OCR 识别到的区域
                    detail=f"Value {value} > {value_threshold}",
                )
            else:
                # 数值小于等于阈值，识别失败
                return None

        except Exception as e:
            # 简单的错误处理
            print(f"数值比较识别错误: {e}")
            return None
