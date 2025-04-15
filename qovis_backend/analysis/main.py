import os
import sys

FILE_ABS_PATH = os.path.dirname(__file__)
ROOT_PATH = os.path.join(FILE_ABS_PATH, os.pardir)
sys.path.append(ROOT_PATH)

if __name__ == '__main__':
    from analysis.algo.algo_r_n import AlgoRandNoop
    from analysis.algo.algo_r_s import AlgoRandStruct
    from analysis.algo.algo_r_tl import AlgoRandTimeline
    from analysis.algo.algo_r_tlc import AlgoRandTimelineCost
    from analysis.algo.algo_ka_tlc import AlgoKeepAllTimelineCost
    from analysis.algo.algo_s_s import AlgoStageStruct

    dataset = 'data2'

    result_path = os.path.join(ROOT_PATH, 'data', dataset, 'result')

    example_list = os.listdir(result_path)
    example_list = list(filter(lambda x: not x.startswith('.'), example_list))
    example_list.sort()
    example_list = example_list[0:2]

    for example_name in example_list:
        result_example_path = os.path.join(result_path, example_name)

        # AlgoRandNoop(result_example_path).execute()
        # AlgoRandStruct(result_example_path).execute()
        # AlgoRandTimeline(result_example_path).execute()
        # AlgoRandTimelineCost(result_example_path).execute()
        # AlgoKeepAllTimelineCost(result_example_path).execute()
        AlgoStageStruct(result_example_path).execute()

        print()


