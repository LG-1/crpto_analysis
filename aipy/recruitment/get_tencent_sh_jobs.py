import requests
import json
from bs4 import BeautifulSoup
import sys
from urllib.parse import urlencode



def get_tencent_job_info(postId):

    """
    if __name__ == "__main__":
        postId = '1902939424958799872'
        job_info = get_tencent_job_info(postId)

        # 保存结果
        with open('tencent_job_api.json', 'w', encoding='utf-8') as f:
            json.dump(job_info, f, ensure_ascii=False, indent=2)

        print("通过API成功获取职位信息并保存为tencent_job_api.json")
        __result__ = {
            'status': 'success',
            'job_info': job_info,
            'file_path': 'tencent_job_api.json'
        }

    """


    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/json'
    }

    # 尝试通过腾讯招聘API获取数据
    api_url = "https://careers.tencent.com/tencentcareer/api/post/ByPostId"
    params = {
        'postId': postId,
        'language': 'zh-cn'
    }

    try:
        response = requests.get(api_url, headers=headers, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()

        # 提取关键信息
        job_info = {
            'PostId': data.get('Data', {}).get('PostId', ''),
            '更新时间': data.get('Data', {}).get('LastUpdateTime', ''),
            '职位链接': data.get('Data', {}).get('PostURL', ''),
            '职位名称': data.get('Data', {}).get('RecruitPostName', ''),
            '工作地点': data.get('Data', {}).get('LocationName', ''),
            '职位类别': data.get('Data', {}).get('CategoryName', ''),
            '工作职责': data.get('Data', {}).get('Responsibility', ''),
            '岗位要求': data.get('Data', {}).get('Requirement', ''),
            '加分项': data.get('Data', {}).get('ImportantItem', ''),
            '岗位亮点': data.get('Data', {}).get('PostLightItem', ''),
            '公司介绍': data.get('Data', {}).get('Introduction', ''),
            '部门介绍': data.get('Data', {}).get('DepartmentIntroduction', ''),
        }
        return job_info

    except requests.exceptions.RequestException as e:
        print(f"API请求失败: {str(e)}", file=sys.stderr)


def get_tencent_job_list():
    # 设置请求头
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
        'Referer': 'https://careers.tencent.com/'
    }

    # 构建API请求URL
    base_url = 'https://careers.tencent.com/tencentcareer/api/post/Query'
    params = {
        'timestamp': '1716307200000',
        'countryId': '',
        'cityId': '3',  # 3表示shanghai
        'bgIds': '',
        'productId': '',
        'categoryId': '',
        'parentCategoryId': '40001', # 40001表示技术类
        'attrId': '',
        'keyword': '',
        'pageIndex': 1,
        'pageSize': 1000,
        'language': 'zh-cn',
        'area': 'cn'
    }

    try:
        # 发送请求获取职位数据
        response = requests.get(base_url, params=params, headers=headers)
        response.raise_for_status()

        # 解析JSON数据
        data = response.json()
        posts = data.get('Data', {}).get('Posts', [])

        if not posts:
            print("未获取到职位数据", file=sys.stderr)
            __result__ = {'status': 'error', 'message': 'No job data found'}
        else:
            # 格式化职位信息
            jobs = []
            for post in posts:
                # print(post)
                job_info = get_tencent_job_info(post.get('PostId', ''))

                jobs.append(job_info)
            return jobs

    except requests.exceptions.RequestException as e:
        print(f"请求失败: {str(e)}", file=sys.stderr)
        __result__ = {'status': 'error', 'message': str(e)}
    except json.JSONDecodeError as e:
        print(f"JSON解析失败: {str(e)}", file=sys.stderr)
        __result__ = {'status': 'error', 'message': str(e)}
    except Exception as e:
        print(f"发生错误: {str(e)}", file=sys.stderr)
        __result__ = {'status': 'error', 'message': str(e)}


if __name__ == "__main__":
    # 保存到JSON文件
    jobs = get_tencent_job_list()
    file_pth = 'tencent/tencent_sh_jobs.json'
    with open(file_pth, 'w', encoding='utf-8') as f:
        json.dump(jobs, f, ensure_ascii=False, indent=2)

    print(f"成功获取{len(jobs)}个职位信息，已保存到{file_pth}")