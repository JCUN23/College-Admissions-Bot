import discord 
import os
from keep_alive import keep_alive
client = discord.Client()
import csv
#from dataclasses import dataclass
from PIL import Image, ImageFont, ImageDraw 

schools = []

def create_school_data():
  with open('undergrad_admins.csv', newline='') as csvfile:
    reader = csv.reader(csvfile)

    for row in reader:
      if len(row) == 8:
        name = row[0].strip()
        admin_rate = row[1].strip()
        act = row[2].strip()
        sat_m = row[3].strip()
        sat_rw = row[4].strip()
        rank10 = row[5].strip()
        rank25 = row[6].strip()
        rank50 = row[7].strip()
        school = [name, admin_rate, act, sat_m, sat_rw, rank10, rank25, rank50]
        schools.append(school)

async def admission_percent_calculator(message):
  params = message.content.split(',')
  u_school = params[1].strip()
  u_gpa = float(params[2].strip())
  u_sat = params[3].strip()
  if u_sat != "N/A":
    u_sat = float(params[3].strip())
  u_act = params[4].strip()
  if u_act != "N/A":
    u_act = float(params[4].strip())
  match_school = schools[0]
  for school in schools:
    if u_school in school[0]:
      match_school = school
      break
  
  match_rate = float(format(float("0." + match_school[1][0:2]),'.2f'))
  match_ACT = (float(match_school[2][0:2]) + int(match_school[2][-2:])) / 2
  match_SAT = float((int(match_school[3][0:3]) + int(match_school[3][-3:])) / 2 + (int(match_school[4][0:3]) + int(match_school[4][-3:])) / 2)

  admissions_odds = u_gpa / 10
  if u_sat == "N/A" and u_act == "N/A":
    pass
  elif u_sat == "N/A" and u_act != "N/A":
    if u_act > match_ACT:
      admissions_odds += u_act / 360
    elif u_act < match_ACT:
      admissions_odds -= u_act / 360
    elif u_act == match_ACT:
      admissions_odds += 0
  elif u_sat != "N/A" and u_act == "N/A":
    if u_sat > match_SAT:
      admissions_odds += u_sat / 16000
    elif u_sat < match_SAT:
      admissions_odds -= u_sat / 16000
    elif u_sat == match_SAT:
      admissions_odds += 0
  else:
    if u_act > match_ACT:
      admissions_odds += u_act / 720
    elif u_act < match_ACT:
      admissions_odds -= u_act / 720
    elif u_act == match_ACT:
      admissions_odds += 0
    if u_sat > match_SAT:
      admissions_odds += u_sat / 32000
    elif u_sat < match_SAT:
      admissions_odds -= u_sat / 32000
    elif u_sat == match_SAT:
      admissions_odds += 0

  if match_rate < 0.5:
    if (admissions_odds - match_rate) > match_rate:
      admissions_odds -= match_rate / 4
    elif (admissions_odds - match_rate) < match_rate and admissions_odds > match_rate:
      admissions_odds -= match_rate / 3
    elif admissions_odds < match_rate:
      admissions_odds -= match_rate / 2
    
  if match_rate > 0.5:
    if (match_rate - admissions_odds) < 0.10:
      admissions_odds += match_rate / 2
    elif (match_rate - admissions_odds ) < .25:
      admissions_odds += match_rate / 3
    elif admissions_odds < match_rate:
      admissions_odds += match_rate / 2
    
  
  admissions_odds_format = float(format(admissions_odds,'.2f'))
  admissions_odds_format *= 100
  printer = str(admissions_odds_format) + "%"
  W = 1920
  H = 1080
  my_image = Image.open('template.jpg')
  my_image = my_image.convert('RGB')
  font = ImageFont.truetype('DejaVuSerif-Bold.ttf', 100)
  font2 = ImageFont.truetype('DejaVuSerif-Bold.ttf', 150)
  if admissions_odds < .25:
    color = [255,0,0]
  elif admissions_odds > .25 and admissions_odds < .5:
    color = [255,191,0]
  else:
    color = [0,255,0]
  image_editable = ImageDraw.Draw(my_image)
  text_width, text_height = image_editable.textsize(str(match_school[0]))
  position1 = ((W-text_width)/2-4*text_width,(H-text_height)/2 - 250)  
  position = ((W-text_width)/2-1.5*text_width,(H-text_height)/2)  
  image_editable.text(position1, match_school[0], (255, 255, 255), font=font)
  image_editable.text(position, printer, (color[0],color[1],color[2]), font=font2)
  my_image.save("result.jpg")
  await message.channel.send(file=discord.File('result.jpg'))

@client.event
async def on_ready():
  print('We have logged in as {0.user}'.format(client))
  create_school_data()

@client.event
async def on_message(message):

  if message.content == "$ca":
    await message.channel.send("To calculate the acceptance probability of a school, type: '$ca admission, 'the school you want to check', 'gpa', 'sat', 'act''")
    await message.channel.send("To find the school that is the best fit for you, type: '$ca bestfit, 'state you want to be in', 'intended major', 'gpa', 'sat', 'act''")
    #await message.channel.send("To see a list of schools to choose from, type $ca list")
    await message.channel.send("If there are entries you wish to leave blank, enter N/A for that space.")
    await message.channel.send("Made by Josh Cunningham")

  if message.content.startswith("$ca list"):
    file1 = open("school-list.txt", "w")
    lines = []
    for school in schools:
        line = school[0] + "\n"
        lines.append(line)
    file1.writelines(lines)  
    file1.close() 
    await message.channel.send(file=discord.File('school-list.txt'))

  if message.content.startswith("$ca admission"):
    await admission_percent_calculator(message)
    
  # if message.content.startswith("$ca bestfit"):
  #   params = message.content.split(' ')
  #   location = params[2]
  #   major = params[3]
  #   gpa = params[4]
  #   sat = params[5]
  #   act = params[6]
    


keep_alive()
client.run(os.getenv('TOKEN'))
