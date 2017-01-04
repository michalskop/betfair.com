# scrapes odds from betfair.org and updates github datapackages

import csv
import datapackage  # v0.8.3
import datetime
import json
import git
import os
import requests

import betfair_com_scraper_utils as utils
import settings

data_path = "data/"  # from this script to data

# repo settings
repo = git.Repo(settings.git_dir)
git_ssh_identity_file = settings.ssh_file
o = repo.remotes.origin
git_ssh_cmd = 'ssh -i %s' % git_ssh_identity_file

total_groups = 0
for fdir in settings.betfair_dirs:
    da = utils.scrape_races(fdir)
    for roww in da:
        dat = utils.scrape_subraces(roww['href'])
        for row in dat:
            date = datetime.datetime.utcnow().isoformat()
            data = utils.scrape_race(row['identifier'])
            # load or create datapackage
            try:
                # load datapackage
                datapackage_url = settings.project_url + data_path + row['identifier'] + "/datapackage.json"
                dp = datapackage.DataPackage(datapackage_url)
            except:
                # create datapackage
                dp = datapackage.DataPackage()
                urldp = settings.project_url + "datapackage_prepared.json"
                rdp = requests.get(urldp)
                prepared = rdp.json()
                dp.descriptor['name'] = "betfair_com_" + row['identifier']
                dp.descriptor['title'] = roww['title'] + " - " + row['title'] + " - odds from betfair.com"
                dp.descriptor['description'] = "Scraped odds from betfair.com for: " + roww['title'] + " - " + row['title']
                for k in prepared:
                    dp.descriptor[k] = prepared[k]
                if not os.path.exists(settings.git_dir + data_path + row['identifier']):
                    os.makedirs(settings.git_dir + data_path + row['identifier'])
                with open(settings.git_dir + data_path + row['identifier'] + '/datapackage.json', 'w') as fout:
                    fout.write(dp.to_json())
                repo.git.add(settings.git_dir + data_path + row['identifier'] + '/datapackage.json')
                with open(settings.git_dir + data_path + row['identifier'] + '/odds.csv', "w") as fout:
                    header = []
                    for resource in dp.resources:
                        if resource.descriptor['name'] == 'odds':
                            for field in resource.descriptor['schema']['fields']:
                                header.append(field['name'])
                    dw = csv.DictWriter(fout, header)
                    dw.writeheader()
                repo.git.add(settings.git_dir + data_path + row['identifier'] + '/market.csv')
                with open(settings.git_dir + data_path + row['identifier'] + '/market.csv', "w") as fout:
                    header = []
                    for resource in dp.resources:
                        if resource.descriptor['name'] == 'market':
                            for field in resource.descriptor['schema']['fields']:
                                header.append(field['name'])
                    dw = csv.DictWriter(fout, header)
                    dw.writeheader()
                repo.git.add(settings.git_dir + data_path + row['identifier'] + '/market.csv')

            # add data
            with open(settings.git_dir + data_path + row['identifier'] + '/odds.csv', "a") as fout:
                header = []
                for resource in dp.resources:
                    if resource.descriptor['name'] == 'odds':
                        for field in resource.descriptor['schema']['fields']:
                            header.append(field['name'])
                dw = csv.DictWriter(fout, header)

                for bet in data['runners']:
                    if bet['state']['status'] == 'ACTIVE':
                        item = {
                            'date': date,
                            'title': bet['description']['runnerName'],
                            'identifier': bet['selectionId']
                        }
                        try:
                            item['odds'] = bet['state']['lastPriceTraded']
                        except:
                            item['odds'] = ''
                        try:
                            item['available_to_back_0'] = bet['exchange']['availableToBack'][0]['price']
                        except:
                            item['available_to_back_0'] = ''
                        try:
                            item['available_to_back_1'] = bet['exchange']['availableToBack'][1]['price']
                        except:
                            item['available_to_back_1'] = ''
                        try:
                            item['available_to_back_2'] = bet['exchange']['availableToBack'][2]['price']
                        except:
                            item['available_to_back_2'] = ''
                        try:
                            item['available_to_lay_0'] = bet['exchange']['availableTLayoBack'][0]['price']
                        except:
                            item['available_to_lay_0'] = ''
                        try:
                            item['available_to_lay_1'] = bet['exchange']['availableTLayoBack'][1]['price']
                        except:
                            item['available_to_lay_1'] = ''
                        try:
                            item['available_to_lay_2'] = bet['exchange']['availableTLayoBack'][2]['price']
                        except:
                            item['available_to_lay_2'] = ''
                        try:
                            item['available_to_back_0_size'] = bet['exchange']['availableToBack'][0]['size']
                        except:
                            item['available_to_back_0_size'] = ''
                        try:
                            item['available_to_back_1_size'] = bet['exchange']['availableToBack'][1]['size']
                        except:
                            item['available_to_back_1_size'] = ''
                        try:
                            item['available_to_back_2_size'] = bet['exchange']['availableToBack'][2]['size']
                        except:
                            item['available_to_back_2_size'] = ''
                        try:
                            item['available_to_lay_0_size'] = bet['exchange']['availableTLayoBack'][0]['size']
                        except:
                            item['available_to_lay_0_size'] = ''
                        try:
                            item['available_to_lay_1_size'] = bet['exchange']['availableTLayoBack'][1]['size']
                        except:
                            item['available_to_lay_1_size'] = ''
                        try:
                            item['available_to_lay_2_size'] = bet['exchange']['availableTLayoBack'][2]['size']
                        except:
                            item['available_to_lay_2_size'] = ''

                        dw.writerow(item)
            repo.git.add(settings.git_dir + data_path + row['identifier'] + '/odds.csv')

            with open(settings.git_dir + data_path + row['identifier'] + '/market.csv', "a") as fout:
                header = []
                for resource in dp.resources:
                    if resource.descriptor['name'] == 'market':
                        for field in resource.descriptor['schema']['fields']:
                            header.append(field['name'])
                dw = csv.DictWriter(fout, header)

                ro = data['state']
                item = {
                    'date': date,
                    'date_bet': row['date'],
                    'bet_delay': ro['betDelay'],
                    'bsp_reconciled': ro['bspReconciled'],
                    'complete': ro['complete'],
                    'inplay': ro['inplay'],
                    'number_of_winners': ro['numberOfWinners'],
                    'number_of_runners': ro['numberOfRunners'],
                    'number_of_active_runners': ro['numberOfActiveRunners'],
                    'total_matched': ro['totalMatched'],
                    'total_available': ro['totalAvailable'],
                    'cross_matching': ro['crossMatching'],
                    'runners_voidable': ro['runnersVoidable'],
                    'version': ro['version'],
                    'status': ro['status']
                }
                try:
                    item['last_match_time'] = ro['lastMatchTime']
                except:
                    item['last_match_time'] = ''
                dw.writerow(item)
            repo.git.add(settings.git_dir + data_path + row['identifier'] + '/market.csv')

            total_groups += 1

# commit to github
with repo.git.custom_environment(GIT_COMMITTER_NAME=settings.bot_name, GIT_COMMITTER_EMAIL=settings.bot_email):
    repo.git.commit(message="happily updating data %s groups of bets" % (str(total_groups)), author="%s <%s>" % (settings.bot_name, settings.bot_email))
with repo.git.custom_environment(GIT_SSH_COMMAND=git_ssh_cmd):
    o.push()
