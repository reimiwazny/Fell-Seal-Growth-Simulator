import PySimpleGUI as sg
import json
from sys import exit
from random import choice

sg.theme('darkpurple7')

#Stat gains per level are randomly 90%/100%/110% of listed value
#max level is 99
#max speed is 250
#max HP/MP is 999
#max ATK/DEF/RES/MIND is 600
#max Evade is 50
#max Crit is 100
#max effective elemental resist is 200

STAT_GAIN_RAND = (0.9, 1, 1.1)
LEV_MAX = 99
SPEED_MAX = 250
HP_MP_MAX = 999
CORESTAT_MAX = 600
EVADE_MAX = 50
CRIT_MAX = 100
ELEM_MAX = 200
MAX_STATS = [
			CORESTAT_MAX,
			CORESTAT_MAX, 
			CORESTAT_MAX, 
			CORESTAT_MAX, 
			SPEED_MAX, 
			HP_MP_MAX, 
			HP_MP_MAX]

job_data = {}
starting_job = ''
char_level = 1

start_job = ''
level_data = ''
stat_data = ''

job_levels = {}

mastered_core = [] #list of mastered standard jobs
mastered_other = [] #list of mastered special/story/mod jobs

master_tt = 'Select this if the current job is mastered.'
initial_tt = 'Select the job the character will\nbe at creation/level reset.'

std_jobs_list = ('Mercenary', 'Knight', 'Templar', 'Duelist', 'Reaver',
			'Assassin', 'Ranger', 'Scoundrel', 'Gunner', 'Peddler',
			'Mender', 'Alchemystic', 'Sorcerer', 'Plague Doctor',
			'Wizard', 'Druid', 'Fellblade', 'Warmage', 'Gambler',
			'Gadgeteer', 'Samurai', 'Wrangler', 'Beastmaster')

sp_jobs_list = ('Lich', 'Vessel', 'Lord', 'Princess','Werewolf', 
			'Vampire', 'Anatomist', 'Marked', 'Demon Knight',
			'The Exiled', 'Spymaster', 'Bounty Hunter')

jobs_list = []


def calc_stats(s_job, jlvls, mastered_std, mastered_other, stat_maximums=MAX_STATS):
	masteries = list(mastered_other) + list(mastered_std)
	detail_str = f'Starting Job:\n{s_job}\n' + '-'*32 + '\nJobs Leveled:\n'
	stats_str = ''
	min_gro = [0,0,0,0,0,0,0]
	avg_gro = [0,0,0,0,0,0,0] #0 - atk, 1 - def, 2 - mind, 3 - res, 4 - spd, 5 - hp, 6 - mp
	max_gro = [0,0,0,0,0,0,0]

	b_atk = job_data[s_job]['b_atk']
	b_def = job_data[s_job]['b_def']
	b_mnd = job_data[s_job]['b_mnd']
	b_res = job_data[s_job]['b_res']
	b_spd = job_data[s_job]['b_spd']
	b_hp = job_data[s_job]['b_hp']
	b_mp = job_data[s_job]['b_mp']

	m_atk = 0
	m_def = 0
	m_mnd = 0
	m_res = 0
	m_spd = 0
	m_hp = 0
	m_mp = 0
	m_crit = 0
	m_eva = 0
	m_elem = 0
	m_holy = 0
	m_dark = 0

	base_stats = [b_atk, b_def, b_mnd, b_res, b_spd, b_hp, b_mp]

	g_atk_min = 0
	g_atk_avg = 0
	g_atk_max = 0

	g_def_min = 0
	g_def_avg = 0
	g_def_max = 0

	g_mnd_min = 0
	g_mnd_avg = 0
	g_mnd_max = 0

	g_res_min = 0
	g_res_avg = 0
	g_res_max = 0

	g_spd_min = 0
	g_spd_avg = 0
	g_spd_max = 0

	g_hp_min = 0
	g_hp_avg = 0
	g_hp_max = 0

	g_mp_min = 0
	g_mp_avg = 0
	g_mp_max = 0

	for j in jlvls:
		if jlvls[j] != 0:
			detail_str += f'{j}: {jlvls[j]} levels\n'
		levels = jlvls[j]
		g_atk_min += float(job_data[j]['g_atk']) * 0.9 * levels
		g_atk_avg += float(job_data[j]['g_atk']) * levels 
		g_atk_max += float(job_data[j]['g_atk']) * 1.1 * levels

		g_def_min += float(job_data[j]['g_def']) * 0.9 * levels
		g_def_avg += float(job_data[j]['g_def']) * levels
		g_def_max += float(job_data[j]['g_def']) * 1.1 * levels

		g_mnd_min += float(job_data[j]['g_mnd']) * 0.9 * levels
		g_mnd_avg += float(job_data[j]['g_mnd']) * levels
		g_mnd_max += float(job_data[j]['g_mnd']) * 1.1 * levels

		g_res_min += float(job_data[j]['g_res']) * 0.9 * levels
		g_res_avg += float(job_data[j]['g_res']) * levels
		g_res_max += float(job_data[j]['g_res']) * 1.1 * levels

		g_spd_min += float(job_data[j]['g_spd']) * 0.9 * levels
		g_spd_avg += float(job_data[j]['g_spd']) * levels
		g_spd_max += float(job_data[j]['g_spd']) * 1.1 * levels

		g_hp_min += float(job_data[j]['g_hp']) * 0.9 * levels
		g_hp_avg += float(job_data[j]['g_hp']) * levels
		g_hp_max += float(job_data[j]['g_hp']) * 1.1 * levels

		g_mp_min += float(job_data[j]['g_mp']) * 0.9 * levels
		g_mp_avg += float(job_data[j]['g_mp']) * levels
		g_mp_max += float(job_data[j]['g_mp']) * 1.1 * levels

		min_pot = (g_atk_min, g_def_min, g_mnd_min, g_res_min,g_spd_min,g_hp_min,g_mp_min)
		max_pot = (g_atk_max, g_def_max, g_mnd_max, g_res_max,g_spd_max,g_hp_max,g_mp_max)
		avg_pot = (g_atk_avg, g_def_avg, g_mnd_avg, g_res_avg,g_spd_avg,g_hp_avg,g_mp_avg)


	if masteries:
		for job in masteries:
			m_atk += job_data[job]['mastery']['m_atk']
			m_def += job_data[job]['mastery']['m_def']
			m_mnd += job_data[job]['mastery']['m_mnd']
			m_res += job_data[job]['mastery']['m_res']
			m_spd += job_data[job]['mastery']['m_spd']
			m_hp += job_data[job]['mastery']['m_hp']
			m_mp += job_data[job]['mastery']['m_mp']
			m_crit += job_data[job]['mastery']['m_crit']
			m_eva += job_data[job]['mastery']['m_eva']
			m_elem += job_data[job]['mastery']['m_elem']
			m_holy += job_data[job]['mastery']['m_holy']
			m_dark += job_data[job]['mastery']['m_dark']
	else:
		pass

	mastery_bonus = [m_atk, m_def, m_mnd, m_res, m_spd, m_hp, m_mp]

	detail_str += '-' * 32 + (
		'\nTotal Mastery Bonus:\n'
		f'ATK: {m_atk}\n'
		f'DEF: {m_def}\n'
		f'MND: {m_mnd}\n'
		f'RES: {m_res}\n'
		f'SPD: {m_spd}\n'
		f'Crit: {m_crit}%\n'
		f'Evade: {m_eva}%\n'
		f'Fir/Wat/Thun/Ert resistance: {m_elem}%\n'
		f'Light resistance: {m_holy}\n'
		f'Dark resistance: {m_dark}\n'
		)


	for x in range(7):
		min_gro[x] = min((min_gro[x] + min_pot[x] + base_stats[x]), stat_maximums[x]) + mastery_bonus[x]  
		max_gro[x] = min((max_gro[x] + max_pot[x] + base_stats[x]), stat_maximums[x]) + mastery_bonus[x]
		avg_gro[x] = min((avg_gro[x] + avg_pot[x] + base_stats[x]), stat_maximums[x]) + mastery_bonus[x]

	window['JLVLS'].update(detail_str)
	stats_str = (
				f'Final Stats:\n'
				'Values are rounded to 2 decimal places.\n'
				'Average values are shown in ()\n'
				f'ATK: {min_gro[0]:.2f}~{max_gro[0]:.2f} ({avg_gro[0]:.2f})\n'
				f'DEF: {min_gro[1]:.2f}~{max_gro[1]:.2f} ({avg_gro[1]:.2f})\n'
				f'MND: {min_gro[2]:.2f}~{max_gro[2]:.2f} ({avg_gro[2]:.2f})\n'
				f'RES: {min_gro[3]:.2f}~{max_gro[3]:.2f} ({avg_gro[3]:.2f})\n'
				f'SPD: {min_gro[4]:.2f}~{max_gro[4]:.2f} ({avg_gro[4]:.2f})\n'
				f'HP: {min_gro[5]:.2f}~{max_gro[5]:.2f} ({avg_gro[5]:.2f})\n'
				f'MP: {min_gro[6]:.2f}~{max_gro[6]:.2f} ({avg_gro[6]:.2f})\n'
				f'Crit: {m_crit}%\n'
				f'Evasion: {m_eva}%\n'
				f'Fir/Wat/Thun/Ert resistance: {m_elem}%\n'
				f'Light resistance: {m_holy}%\n'
				f'Dark resistance: {m_dark}%\n'
				)
	window['TSTATS'].update(stats_str)

def info_window():

	layout = [	[sg.Text('Fell Seal Growth Simulator')],
				[sg.Text('Programmed by Reimi Wazny')],
				[sg.Text('Powered by Python and PySimpleGUI')],
				[sg.Text('')],
				[sg.Multiline('The author of this program is in no way associated with'
					' 6 Eyes Studios or Fulqrum Publishing and does not claim any'
					' ownership of \"Fell Seal: Arbiter\'s Mark" or the contents whereof.'
					' \n\nThis program is provided freely as a FAN WORK, and is not to be'
					' sold or monetized in any way.', size=(44,7), disabled=True, no_scrollbar=True)],
				[sg.OK()]	]

	window = sg.Window('About', layout, font=('any', 15), modal=True, element_justification='center')

	while True:
		event, values = window.read()
		if event in (sg.WIN_CLOSED, 'OK'):
			break

	window.close()

try:
	with open('job_growths.dat', 'r') as file:
		job_data = json.load(file)
		jobs_list = list(job_data.keys())
		jobs_list.sort()
		for job in jobs_list:
			job_levels.update({job:0})
except FileNotFoundError:
	sg.popup('Cannot find job_growths.dat. Exiting program.',title='Error',font=('any',15))
	exit()




# selector = [	[sg.Combo(values=jobs_list, default_value='Select starting job...', size=17, readonly=True,enable_events=True, key='INIT_JOB', tooltip=initial_tt)],
# 				[sg.Combo(values=jobs_list, default_value='Select job...', size=17, readonly=True,enable_events=True, key='JOB_SEL'), sg.Push(),sg.Text('Level',size=9), sg.Multiline(char_level,size=(8,1),key='LVL',disabled=True,no_scrollbar=True)],
# 				[sg.Text('Base HP', size=9), sg.Multiline('',size=(8,1),key='b_hp',disabled=True,no_scrollbar=True),sg.Push(),sg.Text('Base MP',size=9), sg.Multiline('',size=(8,1),key='b_mp',disabled=True,no_scrollbar=True)],
# 				[sg.Text('Base ATK', size=9), sg.Multiline('',size=(8,1),key='b_atk',disabled=True,no_scrollbar=True),sg.Push(),sg.Text('Base DEF',size=9), sg.Multiline('',size=(8,1),key='b_def',disabled=True,no_scrollbar=True)],
# 				[sg.Text('Base MND', size=9), sg.Multiline('',size=(8,1),key='b_mnd',disabled=True,no_scrollbar=True),sg.Push(),sg.Text('Base RES',size=9), sg.Multiline('',size=(8,1),key='b_res',disabled=True,no_scrollbar=True)],
# 				[sg.Text('Base SPD', size=9), sg.Multiline('',size=(8,1),key='b_spd',disabled=True,no_scrollbar=True)],
# 				[sg.Text('HP Gain', size=9), sg.Multiline('',size=(8,1),key='g_hp',disabled=True,no_scrollbar=True),sg.Push(),sg.Text('MP Gain',size=9), sg.Multiline('',size=(8,1),key='g_mp',disabled=True,no_scrollbar=True)],
# 				[sg.Text('ATK Gain', size=9), sg.Multiline('',size=(8,1),key='g_atk',disabled=True,no_scrollbar=True),sg.Push(),sg.Text('DEF Gain',size=9), sg.Multiline('',size=(8,1),key='g_def',disabled=True,no_scrollbar=True)],
# 				[sg.Text('MND Gain', size=9), sg.Multiline('',size=(8,1),key='g_mnd',disabled=True,no_scrollbar=True),sg.Push(),sg.Text('RES Gain',size=9), sg.Multiline('',size=(8,1),key='g_res',disabled=True,no_scrollbar=True)],
# 				[sg.Text('SPD Gain', size=9), sg.Multiline('',size=(8,1),key='g_spd',disabled=True,no_scrollbar=True)],
# 				[sg.Text('Levels to gain in this job:'),sg.Push(),  sg.Input('',size=(8,1),key='GLV',enable_events=True)],
# 				[sg.Checkbox('Master Job', key='MASTER',enable_events=True,tooltip=master_tt), sg.Checkbox('Master All', key='M_ALL',enable_events=True, tooltip='Set all standard jobs as being mastered.'), 
# 				sg.Push(), sg.Button('Add', size=5, tooltip='Add the specified number of levels in this job.'),
# 				sg.Button('Reset', tooltip='Reset the character\'s settings.')]]

selector = [	[sg.Combo(values=jobs_list, default_value='Select starting job...', size=17, readonly=True,enable_events=True, key='INIT_JOB', tooltip=initial_tt, pad=((5,6),(5,5))), sg.Push(), sg.Combo(values=jobs_list, default_value='Select job...', size=17, readonly=True,enable_events=True, key='JOB_SEL'),sg.Push(), sg.Text('Level',size=9), sg.Multiline(char_level,size=(8,1),key='LVL',disabled=True,no_scrollbar=True)],
				[sg.Text('Base HP', size=9), sg.Multiline('',size=(6,1),key='b_hp',disabled=True,no_scrollbar=True),sg.Text('HP Gain', size=9), sg.Multiline('',size=(6,1),key='g_hp',disabled=True,no_scrollbar=True),sg.Text('Mastery HP', size=12), sg.Multiline('',size=(4,1),key='m_hp',disabled=True,no_scrollbar=True), sg.Text('Mastery Crit', size=12), sg.Multiline('',size=(4,1),key='m_crit',disabled=True,no_scrollbar=True)],
				[sg.Text('Base MP',size=9), sg.Multiline('',size=(6,1),key='b_mp',disabled=True,no_scrollbar=True),sg.Text('MP Gain',size=9), sg.Multiline('',size=(6,1),key='g_mp',disabled=True,no_scrollbar=True),sg.Text('Mastery MP', size=12), sg.Multiline('',size=(4,1),key='m_mp',disabled=True,no_scrollbar=True), sg.Text('Mastery Evade', size=12), sg.Multiline('',size=(4,1),key='m_eva',disabled=True,no_scrollbar=True)],
				[sg.Text('Base ATK', size=9), sg.Multiline('',size=(6,1),key='b_atk',disabled=True,no_scrollbar=True),sg.Text('ATK Gain', size=9), sg.Multiline('',size=(6,1),key='g_atk',disabled=True,no_scrollbar=True), sg.Text('Mastery ATK', size=12), sg.Multiline('',size=(4,1),key='m_atk',disabled=True,no_scrollbar=True), sg.Text('M. Elem Res', size=12), sg.Multiline('',size=(4,1),key='m_elem',disabled=True,no_scrollbar=True)],
				[sg.Text('Base DEF',size=9), sg.Multiline('',size=(6,1),key='b_def',disabled=True,no_scrollbar=True),sg.Text('DEF Gain',size=9), sg.Multiline('',size=(6,1),key='g_def',disabled=True,no_scrollbar=True), sg.Text('Mastery DEF', size=12), sg.Multiline('',size=(4,1),key='m_def',disabled=True,no_scrollbar=True), sg.Text('M. Light Res', size=12), sg.Multiline('',size=(4,1),key='m_holy',disabled=True,no_scrollbar=True)],
				[sg.Text('Base MND', size=9), sg.Multiline('',size=(6,1),key='b_mnd',disabled=True,no_scrollbar=True),sg.Text('MND Gain', size=9), sg.Multiline('',size=(6,1),key='g_mnd',disabled=True,no_scrollbar=True), sg.Text('Mastery MND', size=12), sg.Multiline('',size=(4,1),key='m_mnd',disabled=True,no_scrollbar=True), sg.Text('M. Dark Res', size=12), sg.Multiline('',size=(4,1),key='m_dark',disabled=True,no_scrollbar=True)],
				[sg.Text('Base RES',size=9), sg.Multiline('',size=(6,1),key='b_res',disabled=True,no_scrollbar=True),sg.Text('RES Gain',size=9), sg.Multiline('',size=(6,1),key='g_res',disabled=True,no_scrollbar=True), sg.Text('Mastery RES', size=12), sg.Multiline('',size=(4,1),key='m_res',disabled=True,no_scrollbar=True)],
				[sg.Text('Base SPD', size=9), sg.Multiline('',size=(6,1),key='b_spd',disabled=True,no_scrollbar=True),sg.Text('SPD Gain', size=9), sg.Multiline('',size=(6,1),key='g_spd',disabled=True,no_scrollbar=True), sg.Text('Mastery SPD', size=12), sg.Multiline('',size=(4,1),key='m_spd',disabled=True,no_scrollbar=True)],
				[sg.Checkbox('Master Job', key='MASTER',enable_events=True,tooltip=master_tt), sg.Checkbox('Master All', key='M_ALL',enable_events=True, tooltip='Set all standard jobs as being mastered.'),
				sg.Push(), sg.Text('Levels to gain:'),sg.Input('',size=(8,1),key='GLV',enable_events=True)],
				[sg.Button('About'), sg.Push(), sg.Button('Add', size=5, tooltip='Add the specified number of levels in this job.'),
				sg.Button('Reset', tooltip='Reset the character\'s settings.')]]

stat_window = [	[sg.Multiline('', size=	(32,16),disabled=True, key='TSTATS')]	]
layout = [	 [sg.Frame(title='Stats', layout=stat_window, size=(400,425)),
			sg.Frame(title='Details',layout=[[sg.Multiline('', size=(32,16),disabled=True, key='JLVLS')]], size=(400,425))],
			[sg.Frame(title='Jobs', layout=selector, size=(810,425))]	]
window = sg.Window('Fell Seal Growth Simulator', layout, font=('any', 15), element_padding=5)

job_base_stats = ('b_hp', 'b_mp', 'b_atk','b_def','b_mnd','b_res','b_spd')
job_stats = ('g_hp','g_mp','g_atk','g_def','g_mnd','g_res','g_spd')
job_mastery = ('m_hp','m_mp','m_atk','m_def','m_mnd','m_res','m_spd', 'm_crit', 'm_eva', 'm_elem', 'm_holy', 'm_dark')

while True:
	event, values = window.read()
	if event == sg.WIN_CLOSED:
		break
	if event == 'GLV':
		if values['GLV'].isdecimal() == False:
			window['GLV'].update(values['GLV'][:-1])
	if event == 'INIT_JOB':
		if values['INIT_JOB'] != 'Select starting job...':
			job = values['INIT_JOB']
			starting_job = values['INIT_JOB']
			start_job = f'Starting job: {starting_job}\n'
			for stat in job_base_stats:
				window[stat].update(job_data[job][stat])
			calc_stats(starting_job, job_levels, mastered_core, mastered_other)
	if event == 'JOB_SEL':
		if values['JOB_SEL'] != 'Select job...':
			job = values['JOB_SEL']
			for stat in job_stats:
				window[stat].update(job_data[job][stat])
			for stat in job_mastery:
				window[stat].update(job_data[job]['mastery'][stat])
	if event == 'Add' and values['GLV'] and values['LVL']:
		if values['JOB_SEL'] != 'Select job...':
			g_lv = int(values['GLV'])
			job = values['JOB_SEL']
			if g_lv > 0 and g_lv <= (99 - char_level):
				job_levels[job] += g_lv
				window['LVL'].update(int(values['LVL']) + g_lv)
				window['GLV'].update('')
			calc_stats(starting_job, job_levels, mastered_core, mastered_other)

	if event == 'MASTER':
		job = values['JOB_SEL']
		if values['MASTER'] == True:
			if job != 'Select job...':
				if job in std_jobs_list:
					if job not in mastered_core:
						mastered_core.append(job) 
				else:
					if job not in mastered_other:
						mastered_other.append(job)
		else:
			if job != 'Select job...':
				if job in std_jobs_list:
					if job in mastered_core:
						mastered_core.remove(job) 
				else:
					if job in mastered_other:
						mastered_other.remove(job)
		if values['JOB_SEL'] != 'Select job...' and values['INIT_JOB'] != 'Select starting job...':
			calc_stats(values['INIT_JOB'], job_levels, mastered_core, mastered_other)

	if event == 'M_ALL':
		if values['M_ALL']:
			mastered_core = list(std_jobs_list)
		else:
			mastered_core = []
		if values['JOB_SEL'] != 'Select job...' and values['INIT_JOB'] != 'Select starting job...':
			calc_stats(values['INIT_JOB'], job_levels, mastered_core, mastered_other)


	if event == 'Reset':
		char_level = 0
		for job in jobs_list:
			job_levels.update({job:0})
		window['INIT_JOB'].update('Select starting job...')
		window['JOB_SEL'].update('Select job...')
		window['MASTER'].update(False)
		mastered_core = []
		mastered_other = []
		window['M_ALL'].update(False)
		window['JLVLS'].update('')
		window['TSTATS'].update('')
		window['LVL'].update(1)
		window['GLV'].update('')
		for stat in job_stats:
			window[stat].update('')
		for stat in job_mastery:
			window[stat].update('')

	if event == 'About':
		info_window()



window.close()