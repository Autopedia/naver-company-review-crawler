import pandas as pd
import os
import sys
import time
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from tqdm import tqdm
import re

import signal
import sys

import pickle

import random
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.safari.options import Options as SafariOptions
import time

def main():
    num = 1
    print(num)
    searchable_company = pd.read_csv("SearchableCompany.csv")
    naver_ids = list(searchable_company['naverId'])[1556:]

    company_review_urls = []
    for naver_id in naver_ids:
        url = ''.join(["https://pcmap.place.naver.com/place/", str(naver_id), "/review/visitor"])
        company_review_urls.append(url)

    PROXY = "127.0.0.1:22999"
    PATH = "./geckodriver" #Path to chromedriver (Adjust as needed)
    service = Service(executable_path=PATH)
    chrome_options = webdriver.FirefoxOptions()
    chrome_options.add_argument('--proxy-server=%s' % PROXY)
    driver = webdriver.Firefox(service=service, options=chrome_options)

    count = 0 #
    current = 0 #현재 진행 상황

    goal = len(company_review_urls) #총 식당 수

    #데이터 프레임으로 만들 빈 리스트 생성
    rev_list=[]

    def signal_handler(sig, frame):
        print('You pressed Ctrl+C!')
        with open(f"review{num}.plk", "wb") as fp:   #Pickling
            pickle.dump(rev_list, fp)
        sys.exit(0)

    for i in range(len(company_review_urls)):
        current += 1
        print('진행상황 : ', current,'/',goal,sep="")
        # 식당 리뷰 개별 url 접속
        driver.get(company_review_urls[i])
        time.sleep(1)
        print('현재 수집중인 식당 : ', naver_ids[i])

        #리뷰 더보기 버튼 누르기
        while True:
            try:
                driver.find_element(By.CLASS_NAME, 'lfH3O > a')
                driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
                time.sleep(1)
                driver.execute_script('return document.querySelector("div.lfH3O > a").click()')
                time.sleep(1)

            except NoSuchElementException:
                print("-모든 리뷰 더보기 완료-")
                with open(f"review{num}.plk", "wb") as fp:   #Pickling
                    pickle.dump(rev_list, fp)
                break

        # #식당 평균 별점 수집
        # try:
        #     rating = driver.find_element(By.CSS_SELECTOR, 'span.m7jAR.ohonc > em').text
        #     print('식당 평균 별점 : ', rating)
        #     rev_list.append(
        #         [df['naver_id'][i],
        #          rating
        #          ]
        #     )
        # except:
        #     pass





        #리뷰 데이터 스크래핑을 위한 html 파싱
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')

        try:
            #키워드 리뷰가 아닌 리뷰글 리스트 검색
            review_lists = soup.select('.place_section > .place_section_content > ul > li')

            print('총 리뷰 수 : ', len(review_lists))

            #리뷰 수가 0이 아닌 경우 리뷰 수집
            if len(review_lists) > 0 :

                for j, review in enumerate(review_lists):

                    try:

                        #내용 더보기가 있는 경우 내용 더보기를 눌러주기
                        try:
                            review.find(' div.ZZ4OK > a > span.rvCSr > svg')
                            more_content = review.select(' div.ZZ4OK > a > span.rvCSr > svg')
                            more_content.click()
                            time.sleep(1)

                            #리뷰 정보
                            user_review = review.select(' div.ZZ4OK > a > span')


                            #리뷰 정보가 있는 경우 식당 이름, 평점, 리뷰 텍스트, 작성 시간을 가져와서 데이터 프레임으로 만들기
                            if len(user_review) > 0:
                                rev_list.append(
                                    [
                                        naver_ids[i],
                                        '',
                                        user_review[0].text
                                    ]
                                    )




                        except:
                            #리뷰 정보
                            user_review = review.select(' div.ZZ4OK.IwhtZ > a > span')


                            #리뷰 정보가 있는 경우 식당 이름, 평점, 리뷰 텍스트, 작성 시간을 가져와서 데이터 프레임으로 만들기
                            if len(user_review) > 0:
                                rev_list.append(
                                    [
                                        naver_ids[i],
                                        '',
                                        user_review[0].text
                                    ]
                                    )

                    except NoSuchElementException:
                        print('리뷰 텍스트가 인식되지 않음')
                        continue

            else:
                print('리뷰 선택자가 인식되지 않음')



        # 리뷰가 없는 경우
        except NoSuchElementException:

            # rev_list.append(
            # [
            #     df['naver_id'][i],
            #     rating,
            # ]
            # )
            # time.sleep(2)
            print("리뷰가 존재하지 않음")



        #검색한 창 닫고 검색 페이지로 돌아가기
        # driver.close()
        # driver.switch_to.window(tabs[0])
        print("기본 페이지로 돌아가기")

        # data = pd.read_csv("data.csv", index_col=False)
        # data = pd.concat([data, pd.DataFrame(rev_list, columns=['naver_id', 'rating', 'review'])])
        # data.to_csv("data.csv", index=False)
        signal.signal(signal.SIGINT, signal_handler)

    driver.close()

    with open(f"review{num}.plk", "wb") as fp:   #Pickling
        pickle.dump(rev_list, fp)



    # # 스크래핑한 데이터를 데이터 프레임으로 만들기
    # column = ["naver_id", "rating", "review"]
    # df2 = pd.DataFrame(rev_list, columns=column)

    # df2.drop(['rating'], axis=1).to_csv(f"2000.csv")

if __name__ == "__main__":
    main()