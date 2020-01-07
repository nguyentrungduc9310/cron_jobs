from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import time
import pymysql
from datetime import datetime
import html

# current date and time
now = datetime.now()
date_time = now.strftime("%Y-%m-%d %H:%M:%S")

# browser setup
driver = webdriver.Chrome()
driver.get('https://itviec.com')
time.sleep(10)
# Login page
driver.find_element_by_xpath('//*[@class="pageMenu__link"]').click()
time.sleep(3)
driver.find_element_by_xpath('//*[@id="signin-tab"]/form/div[2]/input').send_keys('ductrungnguyen101193@gmail.com')
driver.find_element_by_xpath('//*[@id="signin-tab"]/form/div[3]/input').send_keys('Anhduc123')
driver.find_element_by_xpath('//*[@id="signin-tab"]/form/div[5]/input[2]').click()
time.sleep(5)
# Click show list jobs
driver.find_element_by_xpath('//*[@id="search_form"]/div[3]/input').click()

# Open all pages
# while driver.find_element_by_xpath('//*[@id="show_more"]/a').is_displayed():
for page in range(60):
    driver.find_element_by_xpath('//*[@id="show_more"]/a').click()
    # Scroll down to bottom
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(10)
# Go to detail job to get info
titles = driver.find_elements_by_xpath('//*[@class="job"]/div/div[2]/div[1]/div/h2/a')

num_items = len(titles)
for i in range(num_items):
    # Open database connection
    db = pymysql.connect("localhost", "root", "", "teawork")

    # prepare a cursor object using cursor() method
    cursor = db.cursor()

    link = titles[i].get_attribute('href')
    driver.execute_script('''window.open("%s","_blank");''' % link)
    # driver.get(link)
    # go to detail
    # titles[i].click()
    # driver.manage().timeouts().pageLoadTimeout(10, TimeUnit.SECONDS)
    time.sleep(5)

    # Switch to just clicked link
    window_name = driver.window_handles[1]
    driver.switch_to.window(window_name=window_name)

    # Prepare SQL query to INSERT a record into the database.

    # Company table:
    # saved infos
    companyName = html.escape(driver.find_element_by_xpath('//*/h3/a').text)
    companyLogo = html.escape(driver.find_element_by_xpath('//*[@class="logo"]/a/img').get_attribute('src'))
    companyIntroduce = html.escape(driver.find_element_by_xpath('//*[@class="basic-info"]/div[1]').text)
    companyCountryName = html.escape(driver.find_element_by_xpath('//*[@class="country-name"]').text)
    companyMemberships = html.escape(driver.find_element_by_xpath('//*[@class="group-icon"]').text)

    sqlInsertCompany = "INSERT INTO teawork.companies(name, image, introduce, country_name, membership, created_by, updated_by, created_at, updated_at) \
                            VALUES ('%s','%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (
        companyName, companyLogo, companyIntroduce, companyCountryName, companyMemberships, 'cronBatch',
        'cronBatch',
        date_time, date_time)

    try:
        # Execute the SQL command
        # check exist row
        checkCompany = """SELECT * FROM teawork.companies where name like %s"""
        cursor.execute(checkCompany, companyName)
        if cursor.rowcount > 0:
            record = cursor.fetchall()
            companyId = record[0][0]
        else:
            cursor.execute(sqlInsertCompany)
            companyId = cursor.lastrowid

        # employment information
        # work type 1: full time, 2: part time
        workType = 1
        reputation = 1
        views = 0
        # test with IT jobs value is 1
        careerId = 1
        jobTitle = html.escape(driver.find_element_by_class_name('job_title').text)
        description = html.escape(driver.find_element_by_class_name('job_description').get_attribute('outerHTML'))
        experienceRequest = html.escape(
            driver.find_element_by_class_name('skills_experience').get_attribute('outerHTML'))
        workplace = html.escape(driver.find_element_by_xpath('//*[@class="address__full-address"]/span').text)
        otherInformation = ""
        try:
            otherInformation = html.escape(
                driver.find_element_by_class_name('love_working_here').get_attribute('outerHTML'))
        except:
            otherInformation = ""
        salary = html.escape(driver.find_element_by_class_name('salary-text').text)

        sqlInsertEmploymentInformation = "INSERT INTO teawork.employment_informations(title, company_id, salary, \
                                             work_type, career_id, views, reputation, description, experience_request, workplace, subsidize, other_information, \
                                             created_by, updated_by, created_at, updated_at) \
                                             VALUES ('%s', '%d', '%s', '%d', '%d', '%d', '%d', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (
            jobTitle, companyId, salary, workType, careerId, views, reputation, description, experienceRequest,
            workplace, '', otherInformation, 'cronBatch', 'cronBatch', date_time,
            date_time)
        cursor.execute(sqlInsertEmploymentInformation)
        lastJobId = cursor.lastrowid

        # check tag exist
        tagNames = driver.find_elements_by_xpath('//*[@class="job_info"]/div[1]/a/span')
        num_itemstag = len(tagNames)
        for y in range(num_itemstag):
            sqlInsertEmploymentInformationTags = "INSERT INTO teawork.employment_informations_tags(job_id, name, created_by, updated_by, created_at, updated_at) \
                                                     VALUES ('%d', '%s', '%s', '%s', '%s', '%s')" % (
                lastJobId, tagNames[y].text, 'cronBatch', 'cronBatch', date_time, date_time)
            cursor.execute(sqlInsertEmploymentInformationTags)

        # Commit your changes in the database
        db.commit()
    except TypeError as e:
        print(e)
        db.rollback()

    # disconnect from server
    db.close()

    # window has been closed after already get info
    time.sleep(2)
    driver.close()

    # Switch to root tab
    window_name = driver.window_handles[0]
    driver.switch_to.window(window_name=window_name)

    # break point for test
    # break
driver.quit()
