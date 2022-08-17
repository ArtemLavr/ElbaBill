import requests as re
import re as regex
import json
import time 
from datetime import datetime,  date, timedelta

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains





months = {
		"января":1,
		"февраля":2,
		"марта":3,
		"апреля":4,
		"мая":5,
		"июня":6,
		"июля":7,
		"августа":8,
		"сентября":9,
		"октября":10,
		"ноября":11,
		"декабря":12
		}


def get_data():
	f = open("data.json", "r")
	data = json.load(f)
	f.close()
	return data


def write_data(data):
	f = open("data.json", "w")
	json.dump(data, f)
	f.close()
	

def bill_add_elba(recepient, bill_num, bill_date, vatnum, orders_info_j,  quit = True):

	options = Options()
	options.headless = True

	driver = webdriver.Firefox(executable_path='C:\geckodriver\geckodriver.exe', options=options)
	
	
	driver.get('https://elba.kontur.ru/')
	time.sleep(5)
	if("ИП" in recepient):
		driver.find_element_by_xpath('//*[@id="Email"]').send_keys(ELBA_LOGIN_2)
		driver.find_element_by_xpath('//*[@id="Password"]').send_keys(ELBA_PASS_2)
	else:
		driver.find_element_by_xpath('//*[@id="Email"]').send_keys(ELBA_LOGIN_1)
		driver.find_element_by_xpath('//*[@id="Password"]').send_keys(ELBA_PASS_1)
	driver.find_element_by_xpath('//*[@id="Password"]').send_keys(Keys.RETURN)
	time.sleep(10)

	time.sleep(5)
	driver.find_element_by_xpath('//*[@id="MainMenu_Documents_LinkText"]').click()
	time.sleep(3)
	driver.find_element_by_xpath('//*[@id="MainMenu_Documents_DocumentsSubmenu_OutgoingDocumentsList_LinkText"]').click()
	time.sleep(5)
	
	driver.find_element_by_xpath('/html/body/form/div[4]/div[1]/div[3]/div[1]/div/div[2]/div[2]/div/div[1]/span').click()
	time.sleep(5)
	driver.find_element_by_xpath('//*[@id="Number"]').clear() # заполняем поле номера счета
	driver.find_element_by_xpath('//*[@id="Number"]').send_keys(bill_num)



	driver.find_element_by_xpath('//*[@id="Date"]').clear() # заполняем поле даты создания счета
	driver.find_element_by_xpath('//*[@id="Date"]').send_keys(bill_date)


	driver.find_element_by_xpath('//*[@id="DocumentContractor_ContractorName"]').click()
	time.sleep(2)
	driver.find_element_by_xpath('//*[@id="DocumentContractor_ContractorName"]').send_keys(vatnum)
	time.sleep(7)

	css_selector = "#DocumentContractorPanel > div:nth-child(1) > div:nth-child(2) > div:nth-child(3) > div:nth-child(1) > span:nth-child(2)"

	if(driver.find_element_by_css_selector(css_selector).is_displayed()):
		driver.find_element_by_css_selector(css_selector).click()
		time.sleep(3)
		driver.find_element_by_xpath('/html/body/div[8]/div/div[2]/div/div/div/div/div[3]/div/div/span/span/button/div/span').click()
		time.sleep(3)
		driver.find_element_by_xpath('/html/body/div[8]/div/div[2]/div/div/div/div/div[3]/div/div[1]/div/div/div/span/span/button/div/span').click()
		time.sleep(3)
	else:
		driver.find_element_by_xpath('/html/body/div[2]/div[4]/div/ul/li[1]').click()
	
	
	i = 1
	for order in orders_info_j['doc']['elem']:
		cost = order['cost']['$'].split()[0]
		info = order['info']['$']

		driver.find_element_by_xpath(f"/html/body/form/div[3]/div[1]/div[3]/div[1]/div/div[2]/div[1]/div[8]/div[1]/table/tbody/tr[{i}]/td[3]/span/span/span/textarea").send_keys(info)
								   
		time.sleep(3)
		driver.find_element_by_xpath(f"/html/body/form/div[3]/div[1]/div[3]/div[1]/div/div[2]/div[1]/div[8]/div[1]/table/tbody/tr[{i}]/td[4]/span/span/span/input").send_keys(1)
									  
		driver.find_element_by_xpath(f"/html/body/form/div[3]/div[1]/div[3]/div[1]/div/div[2]/div[1]/div[8]/div[1]/table/tbody/tr[{i}]/td[5]/div/span/span/span/input").send_keys('-')
		driver.find_element_by_xpath(f"/html/body/form/div[3]/div[1]/div[3]/div[1]/div/div[2]/div[1]/div[8]/div[1]/table/tbody/tr[{i}]/td[9]/span/span/span/input").clear()
		driver.find_element_by_xpath(f"/html/body/form/div[3]/div[1]/div[3]/div[1]/div/div[2]/div[1]/div[8]/div[1]/table/tbody/tr[{i}]/td[9]/span/span/span/input").send_keys(cost)
		
		if(i<len(orders_info_j['doc']['elem'])):
			driver.find_element_by_css_selector('#InvoiceItemsTable_FakeName').click()
			i+=1
			time.sleep(3)

		time.sleep(2)

	driver.find_element_by_xpath("/html/body/form/div[3]/div[1]/div[3]/div[1]/div/div[2]/div[2]/span").click()

	if quit:
		driver.quit()

def elba_bill_make(BILL_ADDRESS):
	
	data = get_data()
	if(BILL_ADDRESS == 'lk.itexo.ru/billmgr'):
		payments  = re.get(f"https://{BILL_ADDRESS}?authinfo={BILL_LOGIN}:{BILL_PASS}&func=payment&filter=on&status=1&paymethod=3,4&project=1,3&out=json", verify = False)
	else:
		payments  = re.get(f"https://{BILL_ADDRESS}?authinfo={BILL_LOGIN}:{BILL_PASS}&func=payment&filter=on&status=1&paymethod=3&project=2&out=json", verify = False)
	payments_j =  payments.json()

	
	

	try:
		for pay in payments_j['doc']['elem']:
			payment_id  = pay['id']['$']
			recepient = pay['recipient_name']['$']

			min_date = datetime(2021, 10, 26)

			bill_date = pay['create_date']['$']   
			bill_date = bill_date.split("-")
			current_bill_date = datetime(int(bill_date[0]),int(bill_date[1]), int(bill_date[2]))
			bill_date = bill_date[2]+'.'+bill_date[1]+'.'+bill_date[0]      #получение даты создания платежа
			

			if(BILL_ADDRESS == 'lk.itexo.ru/billmgr'):
				current_id = data["last_payment_id_it"]
				min_id = 576
			else:
				current_id = data["last_payment_id_wc"]
				min_id = 999

			if (int(payment_id) not in current_id) and (int(payment_id)>min_id):  

				
			
				bill_num = pay['number']['$']               #получение номера платежа
				sender_id = pay['sender_id']['$']
				pay_data= re.get(f"https://{BILL_ADDRESS}?authinfo={BILL_LOGIN}:{BILL_PASS}&func=profile.edit&elid={sender_id}&out=json", verify = False)
				pay_data_j= pay_data.json() 
				vatnum  = pay_data_j['doc']['vatnum']['$']                        # номер ИНН плательщика

				orders_info = re.get(f"https://{BILL_ADDRESS}?authinfo={BILL_LOGIN}:{BILL_PASS}&func=payment.orderinfo&elid={payment_id}&out=json", verify = False)

				orders_info_j = orders_info.json()

				bill_add_elba(recepient, bill_num, bill_date, vatnum, orders_info_j)
				
				if(BILL_ADDRESS == 'lk.itexo.ru/billmgr'):
					data["last_payment_id_it"].append(int(payment_id))
				else:
					data["last_payment_id_wc"].append(int(payment_id))
				
				write_data(data)		

				
	except Exception:
		print("Bill make exception")
		
def elba_act_make(BILL_ADDRESS):

	if(BILL_ADDRESS == 'lk.itexo.ru/billmgr'):
		invoice  = re.get(f"https://{BILL_ADDRESS}?authinfo={BILL_LOGIN}:{BILL_PASS}&func=invoice&filter=on&invoice_status=3&profiletype=2,3&out=json", verify = False)
	else:
		invoice  = re.get(f"https://{BILL_ADDRESS}?authinfo={BILL_LOGIN}:{BILL_PASS}&func=invoice&filter=on&invoice_status=3&company=1&profiletype=2,3&out=json", verify = False)
	invoice_j =  invoice.json()

	
	
	
	

	
	data = get_data()


	for act in invoice_j['doc']['elem']:



		act_id  = act['id']['$']
		company = act['company']['$']

		min_date = datetime(2021, 10, 26)

		act_date = act['cdate']['$']   
		act_date = act_date.split("-")
		current_act_date = datetime(int(act_date[0]),int(act_date[1]), int(act_date[2]))
		act_date = act_date[2]+'.'+act_date[1]+'.'+act_date[0]      #получение даты создания платежа
		
		if(BILL_ADDRESS == 'lk.itexo.ru/billmgr'):
			current_act_id = data["last_act_id_it"]
			min_id=458
		else:
			current_act_id = data["last_act_id_wc"]
			min_id=464
		if (int(act_id) not in current_act_id) and (int(act_id)>min_id):

			options = Options()
			options.headless = True

			driver = webdriver.Firefox(executable_path='C:\geckodriver\geckodriver.exe', options=options)
			
			
			driver.get('https://elba.kontur.ru/')
			time.sleep(5)
			if("ИП" in company):
				driver.find_element_by_xpath('//*[@id="Email"]').send_keys(ELBA_LOGIN_2)
				driver.find_element_by_xpath('//*[@id="Password"]').send_keys(ELBA_PASS_2)
			else:
				driver.find_element_by_xpath('//*[@id="Email"]').send_keys(ELBA_LOGIN_1)
				driver.find_element_by_xpath('//*[@id="Password"]').send_keys(ELBA_PASS_1)
			driver.find_element_by_xpath('//*[@id="Password"]').send_keys(Keys.RETURN)
			time.sleep(10)

		
			act_num = act['number']['$']               #получение номера платежа

			
			
			customer_id = act['customer_id']['$']
		
			act_data= re.get(f"https://{BILL_ADDRESS}?authinfo={BILL_LOGIN}:{BILL_PASS}&func=profile.edit&elid={customer_id}&out=json", verify = False)
			act_data_j= act_data.json() 
			print(act_num)
			if (act_data_j['doc']['vatnum'] == {}):
				driver.quit()
				continue
			vatnum  = act_data_j['doc']['vatnum']['$']                        # номер ИНН плательщика

			time.sleep(3)
			driver.find_element_by_xpath('//*[@id="MainMenu_Documents_LinkText"]').click()
			time.sleep(3)
			driver.find_element_by_xpath('/html/body/form/div[4]/div[1]/div[3]/div[1]/div/div[2]/div[2]/div/span[2]').click()
			time.sleep(5)
			
			
			driver.find_element_by_xpath('//*[@id="Number"]').clear() # заполняем полено номера счета
			driver.find_element_by_xpath('//*[@id="Number"]').send_keys(act_num)



			driver.find_element_by_xpath('//*[@id="Date"]').clear() # заполняем поле даты создания счета
			driver.find_element_by_xpath('//*[@id="Date"]').send_keys(act_date)


			driver.find_element_by_xpath('//*[@id="DocumentContractor_ContractorName"]').click()
			time.sleep(2)
			driver.find_element_by_xpath('//*[@id="DocumentContractor_ContractorName"]').send_keys(vatnum)
			time.sleep(7)

			css_selector = "#DocumentContractorPanel > div:nth-child(1) > div:nth-child(2) > div:nth-child(3) > div:nth-child(1) > span:nth-child(2)"

			if(driver.find_element_by_css_selector(css_selector).is_displayed()):
				driver.find_element_by_css_selector(css_selector).click()
				time.sleep(3)				  
				driver.find_element_by_xpath('/html/body/div[8]/div/div[2]/div/div/div/div/div[3]/div/div/span/span/button/div/span').click()
				time.sleep(3)				  
				driver.find_element_by_xpath('/html/body/div[8]/div/div[2]/div/div/div/div/div[3]/div/div[1]/div/div/div/span/span/button/div/span').click()
				time.sleep(3)
			else:
				driver.find_element_by_xpath('/html/body/div[2]/div[4]/div/ul/li[1]').click()
			
			act_info = re.get(f"https://{BILL_ADDRESS}?authinfo={BILL_LOGIN}:{BILL_PASS}&func=invoice.item&elid={act_id}&out=json", verify = False)
			
			act_info_j = act_info.json()
			i = 1
			for item in act_info_j['doc']['elem']:
				cost = item['amount']['$'].split()[0]
				info = item['name']['$']

				driver.find_element_by_xpath(f"/html/body/form/div[3]/div[1]/div[3]/div[1]/div/div[2]/div[1]/div[8]/div[1]/table/tbody/tr[{i}]/td[3]/span/span/span/textarea").send_keys(info)
										   
				time.sleep(3)
				driver.find_element_by_xpath(f"/html/body/form/div[3]/div[1]/div[3]/div[1]/div/div[2]/div[1]/div[8]/div[1]/table/tbody/tr[{i}]/td[4]/span/span/span/input").send_keys(1)
											  
				driver.find_element_by_xpath(f"/html/body/form/div[3]/div[1]/div[3]/div[1]/div/div[2]/div[1]/div[8]/div[1]/table/tbody/tr[{i}]/td[5]/div/span/span/span/input").send_keys('-')
				driver.find_element_by_xpath(f"/html/body/form/div[3]/div[1]/div[3]/div[1]/div/div[2]/div[1]/div[8]/div[1]/table/tbody/tr[{i}]/td[9]/span/span/span/input").clear()
				driver.find_element_by_xpath(f"/html/body/form/div[3]/div[1]/div[3]/div[1]/div/div[2]/div[1]/div[8]/div[1]/table/tbody/tr[{i}]/td[9]/span/span/span/input").send_keys(cost)
				
				if(i<len(act_info_j['doc']['elem'])):
					driver.find_element_by_css_selector('#InvoiceItemsTable_FakeName').click()
					i+=1
					time.sleep(3)

			driver.find_element_by_xpath("/html/body/form/div[3]/div[1]/div[3]/div[1]/div/div[2]/div[2]/span").click()
			if(BILL_ADDRESS == 'lk.itexo.ru/billmgr'):
				data["last_act_id_it"].append(int(act_id))
			else:
				data["last_act_id_wc"].append(int(act_id))
			
			write_data(data)

			driver.quit()

def change_payment_status(BILL_ADDRESS):

	if(BILL_ADDRESS == 'lk.itexo.ru/billmgr'):
		payments  = re.get(f"https://{BILL_ADDRESS}?authinfo={BILL_LOGIN}:{BILL_PASS}&func=payment&filter=on&status=1&paymethod=4,3&out=json", verify = False)
	else:
		payments  = re.get(f"https://{BILL_ADDRESS}?authinfo={BILL_LOGIN}:{BILL_PASS}&func=payment&filter=on&status=1&paymethod=3&out=json", verify = False)
	payments_j =  payments.json()

	
	
	for ELBA_LOGIN, ELBA_PASS in [(ELBA_LOGIN_1,ELBA_PASS_1),(ELBA_LOGIN_2, ELBA_PASS_2)]:
		options = Options()
		options.headless = True

		driver = webdriver.Firefox(executable_path='C:\geckodriver\geckodriver.exe', options = options)
			
		
		driver.get('https://elba.kontur.ru/')
		time.sleep(5)
		driver.find_element_by_xpath('//*[@id="Email"]').send_keys(ELBA_LOGIN)
		driver.find_element_by_xpath('//*[@id="Password"]').send_keys(ELBA_PASS)
		driver.find_element_by_xpath('//*[@id="Password"]').send_keys(Keys.RETURN)
		
		time.sleep(5)
		driver.find_element_by_xpath('//*[@id="MainMenu_Documents_LinkText"]').click()
		time.sleep(3)
		driver.find_element_by_xpath('//*[@id="MainMenu_Documents_DocumentsSubmenu_OutgoingDocumentsList_LinkText"]').click()
		time.sleep(5)

		input_f = driver.find_element_by_xpath('//*[@id="SearchInput_Query"]')
		time.sleep(5)
		
		try:		
			for pay in payments_j['doc']['elem']:
				payment_id  = pay['id']['$']
				bill_num = pay['number']['$']
				bill_date = pay['create_date_l']['$']
				bill_date = bill_date.split()
				bill_date = bill_date[0]+' '+bill_date[1]
				bill_name = f"Счёт №{bill_num} от {bill_date}"
				print(bill_name)
				input_f.send_keys(bill_name)
				time.sleep(2)
				elem = driver.find_elements_by_xpath('//*[@id="ItemsList_Rows"]/div')
				op = "Оплачен"
				try:
					if (bill_name in elem[0].text and op in elem[0].text):
						re.get(f"https://{BILL_ADDRESS}?authinfo={BILL_LOGIN}:{BILL_PASS}&elid={payment_id}&func=payment.setpaid&out=json", verify = False)

				except Exception:
					print("Нет ткого счета")
				driver.find_element_by_xpath('//*[@id="SearchInput_ResetSearch"]').click()
				time.sleep(1)
		except Exception:
			print("Change paymen exception")
	driver.quit()


def dell_bill_elba(BILL_ADDRESS):
	payments = re.get(f"https://{BILL_ADDRESS}?authinfo={BILL_LOGIN}:{BILL_PASS}&func=payment&filter=on&status=1&paymethod=3&out=json", verify = False)
	payments_j =  payments.json()

	
	
	
	options = Options()
	options.headless = True

	driver = webdriver.Firefox(executable_path='C:\geckodriver\geckodriver.exe', options = options)
		
	
	driver.get('https://elba.kontur.ru/')
	time.sleep(5)
	driver.find_element_by_xpath('//*[@id="Email"]').send_keys(ELBA_LOGIN_1)
	driver.find_element_by_xpath('//*[@id="Password"]').send_keys(ELBA_PASS_1)
	driver.find_element_by_xpath('//*[@id="Password"]').send_keys(Keys.RETURN)
	time.sleep(10)
	

	for pay in payments_j['doc']['elem']:
		payment_id  = pay['id']['$']  
		bill_num = pay['number']['$']  

		bill_date = pay['create_date']['$']   
		bill_date = bill_date.split('-')
		
		current_bill_date = date(int(bill_date[0]),int(bill_date[1]), int(bill_date[2]))
		today_date = datetime.now().date()
		delta = today_date - current_bill_date

		days = delta.days
		if days>30:
			print(payment_id)
			print(bill_num)
			re.get(f"https://{BILL_ADDRESS}?authinfo={BILL_LOGIN}:{BILL_PASS}&elid={payment_id}&func=payment.delete&out=json", verify = False)


			time.sleep(3)
			driver.find_element_by_xpath('//*[@id="MainMenu_Documents_LinkText"]').click()
			time.sleep(3)
			driver.find_element_by_xpath('//*[@id="MainMenu_Documents_DocumentsSubmenu_OutgoingDocumentsList_LinkText"]').click()
			time.sleep(5)

			bill_name = f"Счёт №{bill_num}"

			search_line = driver.find_element_by_xpath('//*[@id="SearchInput_Query"]')	
			search_line.send_keys(bill_name)
			time.sleep(2)
			elements = driver.find_elements_by_xpath('//*[@id="ItemsList_Rows"]/div')

			for elem in elements:
				if (bill_name in elem.text):
					e= elem.find_element_by_class_name("documentsNestedList-document")

					e.click()
					time.sleep(3)
					driver.find_element_by_xpath('//*[@id="DeleteDocumentLink"]').click()
					time.sleep(3)
					driver.find_element_by_xpath('//*[@id="DeleteDocumentConfirmationPopup_AcceptButton"]').click()
					time.sleep(3)

	driver.quit()



def act_generate(BILL_ADDRESS):

	last_day = date.today().replace(day=1) - timedelta(days=1)

	start_day = date.today().replace(day=1) - timedelta(days=last_day.day)

	last_day = f"{last_day.year}-{last_day.month}-{last_day.day}"

	start_day = f"{start_day.year}-{start_day.month}-{start_day.day}"

	
	if(BILL_ADDRESS == 'lk.itexo.ru/billmgr'):
		gen_req_text_1 = f"https://{BILL_ADDRESS}?authinfo={BILL_LOGIN}:{BILL_PASS}&func=invoice.generate&sok=ok&invoice_status=0&summarizeinvoice=0&gentype=all&company=32&profiletype=1,2,3&cdate={last_day}&fromdate={start_day}&todate={last_day}&out=json"
		re.get(gen_req_text_1, verify = False)
		print(res_1.json())

		gen_req_text_2 = f"https://{BILL_ADDRESS}?authinfo={BILL_LOGIN}:{BILL_PASS}&func=invoice.generate&sok=ok&invoice_status=0&summarizeinvoice=0&gentype=all&company=1&profiletype=1,2,3&cdate={last_day}&fromdate={start_day}&todate={last_day}&out=json"
		re.get(gen_req_text_2, verify = False)
		print(res_2.json())
	else:	
		gen_req_text = f"https://{BILL_ADDRESS}?authinfo={BILL_LOGIN}:{BILL_PASS}&func=invoice.generate&sok=ok&invoice_status=0&summarizeinvoice=0&gentype=all&company=1&profiletype=1,2,3&cdate={last_day}&fromdate={start_day}&todate={last_day}&out=json"

		re.get(gen_req_text, verify = False)

	

	last_month_invoice =re.get(f"https://{BILL_ADDRESS}?authinfo={BILL_LOGIN}:{BILL_PASS}&func=invoice&filter=on&fromdate={start_day}&todate={last_day}&out=json", verify = False)

	last_month_invoice_j = last_month_invoice.json()
	
	for act in last_month_invoice_j['doc']['elem']:
		
		act_id  = act['id']['$']  
		
		send_req_text = f"https://{BILL_ADDRESS}?authinfo={BILL_LOGIN}:{BILL_PASS}&func=invoice.send&sok=ok&elid={act_id}&out=json"
		
		re.get(send_req_text, verify = False)


def maney_to_payment():


	options = Options()
	options.headless = True

	driver = webdriver.Firefox(executable_path='C:\geckodriver\geckodriver.exe', options = options)

	driver.get('https://elba.kontur.ru/')
	time.sleep(5)
	driver.find_element_by_xpath('//*[@id="Email"]').send_keys(ELBA_LOGIN_1)
	driver.find_element_by_xpath('//*[@id="Password"]').send_keys(ELBA_PASS_1)
	driver.find_element_by_xpath('//*[@id="Password"]').send_keys(Keys.RETURN)
	time.sleep(10)
	
	driver.find_element_by_xpath('//*[@id="MainMenu_Payments_LinkText"]').click()

	
	phrase = "Связать с документом"
	for i in range(6):
		time.sleep(3)
		elements = driver.find_elements_by_xpath('//*[@id="ItemsList_Rows"]/div')

		for elem in elements:
			if (phrase in elem.text):
				amount =elem.find_element_by_xpath('./div/div/div/div[5]/div').text.strip().replace(" ", "")
				amount = amount.replace(",",".")
				res = elem.find_element_by_xpath('./div/div/div/div[7]/div').text
				res = res.split()
				current_date = datetime(datetime.now().year, months[res[1]], int(res[0]))
				days_delta = datetime.now().date() - current_date.date()
				if (current_date > datetime(2021, 11, 1) and days_delta.days > 7):
					print("YES")
					time.sleep(1)
					driver.execute_script("arguments[0].scrollIntoView();", elem)
					driver.execute_script("arguments[0].click();", elem)
					time.sleep(2)
					driver.find_element_by_xpath('/html/body/div[2]/div[2]/div[2]/form/div/div[5]/div[2]/div[2]/div/div/div/span').click()

					vatnum = driver.find_element_by_xpath('/html/body/div[2]/div[2]/div[2]/form/div/div[5]/div[2]/div[2]/div/div/div/div/div/div[1]/div[2]/span[1]').text

					try:

						print(vatnum)

						profile = re.get(f"https://lk.whitecloud24.ru/billmgr?authinfo=elba:B9b8H0e8&func=profile&filter=on&vatnum={vatnum}&out=json", verify=False)
						
						profile_j= profile.json()
						
						profile_id = profile_j['doc']['elem'][0]['id']['$']

						account_name = profile_j['doc']['elem'][0]['account']['$']

						account = re.get(f"https://lk.whitecloud24.ru/billmgr?authinfo=elba:B9b8H0e8&func=account&filter=on&account={account_name}&out=json", verify=False)

						account_j = account.json()
						
						account_id = account_j['doc']['elem'][0]['id']['$']

						payment_add_result = re.get(f"https://lk.whitecloud24.ru/billmgr?authinfo=elba:B9b8H0e8&amount={amount}&customer_account={account_id}&func=payment.add.pay&paymethod=3&payment_currency=126&profile={profile_id}&sok=ok&out=json", verify=False)

						payment_add_result_j = payment_add_result.json()

						print(payment_add_result_j)

						payment_id = payment_add_result_j['doc']['id'][0]['$']

						print('Payment id:',payment_id)
						pay  = re.get(f"https://lk.whitecloud24.ru/billmgr?authinfo=elba:B9b8H0e8&func=payment&filter=on&id={payment_id}&out=json", verify = False)
						pay = pay.json()
						
						recepient = pay['doc']['elem'][0]['recipient_name']['$']

						bill_date = pay['doc']['elem'][0]['create_date']['$']   
						bill_date = bill_date.split("-")
						current_bill_date = datetime(int(bill_date[0]),int(bill_date[1]), int(bill_date[2]))
						bill_date = bill_date[2]+'.'+bill_date[1]+'.'+bill_date[0]      #получение даты создания платежа

						bill_num = pay['doc']['elem'][0]['number']['$']               #получение номера платежа
						sender_id = pay['doc']['elem'][0]['sender_id']['$']
						
						

						orders_info = re.get(f"https://lk.whitecloud24.ru/billmgr?authinfo=elba:B9b8H0e8&func=payment.orderinfo&elid={payment_id}&out=json", verify = False)

						orders_info_j = orders_info.json()

						


						data = get_data()

						bill_add_elba(recepient, bill_num, bill_date, vatnum, orders_info_j, False)

						data["last_payment_id_wc"].append(int(payment_id))

						write_data(data)

						driver.find_element_by_xpath('//*[@id="ComponentsHost_PaymentEditLightbox_LinkedDocumentsSection_Relations_LinkWithFirstBill"]').click()
						time.sleep(1)
						driver.find_element_by_xpath('/html/body/div[2]/div[2]/div[2]/form/div/div[5]/div[6]/div[2]/div[2]/div[3]/div[2]/div[1]/div/div[1]/div[1]/label/div/div')
						time.sleep(1)
						driver.find_element_by_xpath('/html/body/div[2]/div[2]/div[2]/form/div/div[7]/div[2]/div[3]/span[1]/span/span/span/span').click()
					

					except Exception:
						print("Нет такого ИНН")
					elem.find_element_by_xpath('//*[@id="ComponentsHost_PaymentEditLightbox_CloseLink"]').click()
		driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")				
		next_p = driver.find_element_by_xpath('//*[@id="ItemsList_Paging_ForwardLink"]')
		ActionChains(driver).move_to_element(next_p).click().perform()
		
	driver.quit()


if __name__ == "__main__":
	
	now_hour = datetime.now().hour
	now_minutes = datetime.now().minute
	now_day = datetime.now().day
	
	# if now_hour ==3:
	dell_bill_elba('lk.whitecloud24.ru/billmgr')

	# bills = [ 'lk.whitecloud24.ru/billmgr', 'lk.itexo.ru/billmgr'  ]
	
	
	# if((now_day == 1 ) and (now_hour==5)):
	# 	for bill_adress in bills:
		
	# 		act_generate(bill_adress)


	# for bill_adress in bills:	

	# 	elba_bill_make(bill_adress)
	# 	elba_act_make(bill_adress)
	# 	change_payment_status(bill_adress)
		
	# # maney_to_payment()