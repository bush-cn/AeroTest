import subprocess
import sys

from utils.logger import logger

def run_jacoco_coverage_analyzer(jar_path, exec_file_path, class_files_path, target_class_name, target_method_name=None):
    """
    运行 JacocoCoverageAnalyzer 工具，输出指定类的所有方法的覆盖率或指定方法的覆盖率。

    :param jar_path: JacocoCoverageAnalyzer JAR 文件的路径
    :param exec_file_path: JaCoCo 生成的 .exec 文件路径
    :param class_files_path: 包含目标类文件的目录路径
    :param target_class_name: 目标类的全限定名
    :param target_method_name: 目标方法的名称（可选）
    """
    if '.' in target_class_name:
        target_class_name = target_class_name.replace('.', '/')
    
    command = [
        'java', '-jar', jar_path,
        exec_file_path,
        class_files_path,
        target_class_name
    ]

    if target_method_name:
        command.append(target_method_name)

    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        logger.info(f"run_jacoco_coverage_analyzer Command executed successfully: {' '.join(command)}")
        # print(result.stdout)
        output_lines = result.stdout.split('\n')
        instruction_coverage_result = {}
        branch_coverage_result = {}
        line_coverage_result = {}
        
        # 这里可能会存在方法重载的情况，不过没关系，我们都输出也是可以的
        if target_method_name:
            # Example output:
            # 类名: dev/danvega/runnerz/run/JdbcRunRepository
            # 覆盖率: 1.0
            # 解析输出并格式化为字典
            for line in output_lines:
                if line.startswith('Instruction Coverage:'):
                    cov_percentage = line.split(':')[-1].strip()
                    if cov_percentage == 'NaN':
                        cov_percentage = -1
                    # if target_method_name in instruction_coverage_result:
                    #     logger.warning(f"Duplicate method name found: {target_method_name}")
                    #     instruction_coverage_result["Instruction Coverage"] = [instruction_coverage_result[target_method_name], float(cov_percentage)]
                    # else:
                    if "Instruction Coverage" in instruction_coverage_result:
                        instruction_coverage_result["Instruction Coverage"] = max(instruction_coverage_result["Instruction Coverage"], float(cov_percentage))
                        logger.warning(f"Duplicate method name found: {target_method_name}")
                    else:
                        instruction_coverage_result["Instruction Coverage"] = float(cov_percentage)
                
                if line.startswith('Branch Coverage:'):
                    cov_percentage = line.split(':')[-1].strip()
                    if cov_percentage == 'NaN':
                        cov_percentage = -1
                    # if target_method_name in branch_coverage_result:
                    #     branch_coverage_result["Branch Coverage"] = [branch_coverage_result[target_method_name], float(cov_percentage)]
                    #     logger.warning(f"Duplicate method name found: {target_method_name}")
                    if "Branch Coverage" in branch_coverage_result:
                        branch_coverage_result["Branch Coverage"] = max(branch_coverage_result["Branch Coverage"], float(cov_percentage))
                        # logger.warning(f"Duplicate method name found: {target_method_name}")
                    else:
                        branch_coverage_result["Branch Coverage"] = float(cov_percentage)
                        
                if line.startswith('Line Coverage:'):
                    cov_percentage = line.split(':')[-1].strip()
                    if cov_percentage == 'NaN':
                        cov_percentage = -1
                    # if target_method_name in line_coverage_result:
                    #     logger.warning(f"Duplicate method name found: {target_method_name}")
                    #     line_coverage_result["Line Coverage:"] = [line_coverage_result[target_method_name], float(cov_percentage)]
                    if "Line Coverage" in line_coverage_result:
                        line_coverage_result["Line Coverage"] = max(line_coverage_result["Line Coverage"], float(cov_percentage))
                        # logger.warning(f"Duplicate method name found: {target_method_name}")
                    else:
                        line_coverage_result["Line Coverage"] = float(cov_percentage)

            return {target_method_name: [instruction_coverage_result, branch_coverage_result, line_coverage_result]}
        else:
            # Example output:
            # 类名: io/github/sashirestela/openai/SimpleOpenAIAzure
            # <init>(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/net/http/HttpClient;)V: -1
            # extractDeployment(Ljava/lang/String;)Ljava/lang/String;: 1.0
            # getNewUrl(Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;: 0.9393939393939394
            # getBodyForJson(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)Ljava/lang/Object;: 1.0
            methods_coverage = {}
            current_method = None
            current_coverage = {}

            for line in output_lines:
                if line.startswith('Method name:'):
                    if current_method:
                        methods_coverage[current_method] = current_coverage
                    current_method = line.split(':')[-1].strip()
                    current_coverage = {}
                elif line.startswith('Instruction Coverage:'):
                    cov_percentage = line.split(':')[-1].strip()
                    if cov_percentage == 'NaN':
                        cov_percentage = -1
                    current_coverage['Instruction Coverage'] = float(cov_percentage)
                elif line.startswith('Branch Coverage:'):
                    cov_percentage = line.split(':')[-1].strip()
                    if cov_percentage == 'NaN':
                        cov_percentage = -1
                    current_coverage['Branch Coverage'] = float(cov_percentage)
                elif line.startswith('Line Coverage:'):
                    cov_percentage = line.split(':')[-1].strip()
                    if cov_percentage == 'NaN':
                        cov_percentage = -1
                    current_coverage['Line Coverage'] = float(cov_percentage)

            if current_method:
                methods_coverage[current_method] = current_coverage
            return methods_coverage
    except subprocess.CalledProcessError as e:
        logger.error(f"run_jacoco_coverage_analyzer Command failed: {' '.join(command)}, {e.stdout}")
        # sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 5:
        print("Usage: python run_jacoco_coverage_analyzer.py <jar_path> <exec_file_path> <class_files_path> <target_class_name> [target_method_name]")
        sys.exit(1)

    jar_path = sys.argv[1]
    exec_file_path = sys.argv[2]
    class_files_path = sys.argv[3]
    target_class_name = sys.argv[4]
    target_method_name = sys.argv[5] if len(sys.argv) > 5 else None

    print(run_jacoco_coverage_analyzer(jar_path, exec_file_path, class_files_path, target_class_name, target_method_name))