import PySimpleGUI as sg
import json
from sys import exit
from random import choice

sg.theme('darkpurple7')

STAT_GAIN_RAND = { #Minimum and maximum stat growth multipliers. Note that random
	'MIN': 0.9,    #stat growth variance is NOT a sliding scale - it is either the
	'MAX': 1.1}    #minimum, maximum, or unaffected.

LEV_MAX = 99       #Maximum level
SPEED_MAX = 250	   #Maximum value for speed, before masteries and gear bonus
HP_MP_MAX = 999    #Maximum value for HP/MP, including gear bonuses
CORESTAT_MAX = 600 #Max value for ATK/DEF/MND/RES, excluding mastery/gear bonus
EVADE_MAX = 50     #Max value for Evasion, including mastery/gear bonus
CRIT_MAX = 100     #Max value for critical chance. Values over 100 have no added effect
ELEM_MAX = 200     #Max value for elemental resistance. Values over 100 indicate absorbtion
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

job_levels = {}

mastered_core = [] #list of mastered standard jobs
mastered_other = [] #list of mastered special/story/mod jobs


std_jobs_list = ('Mercenary', 'Knight', 'Templar', 'Duelist', 'Reaver',
			'Assassin', 'Ranger', 'Scoundrel', 'Gunner', 'Peddler',
			'Mender', 'Alchemystic', 'Sorcerer', 'Plague Doctor',
			'Wizard', 'Druid', 'Fellblade', 'Warmage', 'Gambler',
			'Gadgeteer', 'Samurai', 'Wrangler', 'Beastmaster')

sp_jobs_list = ('Lich', 'Vessel', 'Lord', 'Princess','Werewolf', 
			'Vampire', 'Anatomist', 'Marked', 'Demon Knight',
			'The Exiled', 'Spymaster', 'Bounty Hunter')

jobs_list = []


def calc_stats(s_job,
				jlvls,
				mastered_std, 
				mastered_other, 
				stat_maximums=MAX_STATS, 
				max_crit=CRIT_MAX, 
				max_elem=ELEM_MAX, 
				max_eva=EVADE_MAX,
				stat_rand=STAT_GAIN_RAND):
	'''Function which calculates the expected stat growth for a character
	and updates the 'stats' and 'levels' windows accordingly.

	Arguments:

	s_job: String. The initial job a character is created or level reset as.

	jlvls: Dict. A dictionary containing all avaliable jobs as keys, and the
	number of levels gained in each job as an integer value.

	mastered_std: List. A list of all standard jobs that have been marked as
	mastered, as strings. Standard jobs here are defined as those which are
	not exclusive to special characters, which require a badge to access, or
	which come from mods.

	mastered_other: List. A list of all non-standard jobs that have been marked
	as mastered.

	stat_maximum: List. A list containing the maximum values for each of the
	different character stats, as integers.

	max_crit: Integer. Numeric value for the upper limit of critical hit
	chance.

	max_elem: Integer. Numeric value for the upper limit of elemental resistance.

	max_eva: Integer. Numeric value for the upper limit of evasion rate.

	stat_rand: Dict. Dictionary containing the lower and upper stat growth
	multipliers. Note that stat growth randomness is specifically a random
	choice between minimum modifier, no modifier, and maximum modifier.'''
	min_mult = stat_rand['MIN']
	max_mult = stat_rand['MAX']
	masteries = list(mastered_other) + list(mastered_std)
	masteries.sort()
	detail_str = f'Starting Job:\n{s_job}\n' + '-'*32 + '\nJobs Leveled:\n'
	stats_str = ''
	min_gro = [0,0,0,0,0,0,0]
	avg_gro = [0,0,0,0,0,0,0] #0 - atk, 1 - def, 2 - mind, 3 - res, 4 - spd, 5 - hp, 6 - mp
	max_gro = [0,0,0,0,0,0,0]

	b_atk = job_data[s_job]['b_atk'] #initialize base stats according to starting job
	b_def = job_data[s_job]['b_def']
	b_mnd = job_data[s_job]['b_mnd']
	b_res = job_data[s_job]['b_res']
	b_spd = job_data[s_job]['b_spd']
	b_hp = job_data[s_job]['b_hp']
	b_mp = job_data[s_job]['b_mp']

	m_atk = 0 						 #initialize mastery bonus
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

	g_atk_min = 0 #initialize total stat growth minimums, maximums
	g_atk_avg = 0 #and averages
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

	for j in jlvls:														#Iterates through all avaliable jobs and totals
		if jlvls[j] != 0:												#up minimum, maximum, and average stat growths
			detail_str += f'{j}: {jlvls[j]} levels\n'					#based on the number of levels gained.
		levels = jlvls[j]												#Additionally adds a summary of all jobs leveled
		g_atk_min += float(job_data[j]['g_atk']) * min_mult * levels    #to the detail_str for display in the 'JLVLS' window
		g_atk_avg += float(job_data[j]['g_atk']) * levels 
		g_atk_max += float(job_data[j]['g_atk']) * max_mult * levels

		g_def_min += float(job_data[j]['g_def']) * min_mult * levels
		g_def_avg += float(job_data[j]['g_def']) * levels
		g_def_max += float(job_data[j]['g_def']) * max_mult * levels

		g_mnd_min += float(job_data[j]['g_mnd']) * min_mult * levels
		g_mnd_avg += float(job_data[j]['g_mnd']) * levels
		g_mnd_max += float(job_data[j]['g_mnd']) * max_mult * levels

		g_res_min += float(job_data[j]['g_res']) * min_mult * levels
		g_res_avg += float(job_data[j]['g_res']) * levels
		g_res_max += float(job_data[j]['g_res']) * max_mult * levels

		g_spd_min += float(job_data[j]['g_spd']) * min_mult * levels
		g_spd_avg += float(job_data[j]['g_spd']) * levels
		g_spd_max += float(job_data[j]['g_spd']) * max_mult * levels

		g_hp_min += float(job_data[j]['g_hp']) * min_mult * levels
		g_hp_avg += float(job_data[j]['g_hp']) * levels
		g_hp_max += float(job_data[j]['g_hp']) * max_mult * levels

		g_mp_min += float(job_data[j]['g_mp']) * min_mult * levels
		g_mp_avg += float(job_data[j]['g_mp']) * levels
		g_mp_max += float(job_data[j]['g_mp']) * max_mult * levels

		min_pot = (g_atk_min, g_def_min, g_mnd_min, g_res_min,g_spd_min,g_hp_min,g_mp_min)
		max_pot = (g_atk_max, g_def_max, g_mnd_max, g_res_max,g_spd_max,g_hp_max,g_mp_max)
		avg_pot = (g_atk_avg, g_def_avg, g_mnd_avg, g_res_avg,g_spd_avg,g_hp_avg,g_mp_avg)


	if masteries:										#Iterates through all mastered jobs and
		for job in masteries:							#totals up their mastery bonuses
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

	mastery_bonus = [m_atk, m_def, m_mnd, m_res, m_spd, m_hp, m_mp]

	for x in range(5):																						#Ensures stat growths have not exceeded the
		min_gro[x] = min((min_gro[x] + min_pot[x] + base_stats[x]), stat_maximums[x]) + mastery_bonus[x]  	#respective caps, then adds mastery bonuses.
		max_gro[x] = min((max_gro[x] + max_pot[x] + base_stats[x]), stat_maximums[x]) + mastery_bonus[x]	#Applies to ATK, DEF, MND, RES, and SPD.
		avg_gro[x] = min((avg_gro[x] + avg_pot[x] + base_stats[x]), stat_maximums[x]) + mastery_bonus[x]

	for x in range(5,7):
		min_gro[x] = min((min_gro[x] + min_pot[x] + base_stats[x] + mastery_bonus[x]), stat_maximums[x])   #Ensures that HP and MP have not exceeded their
		max_gro[x] = min((max_gro[x] + max_pot[x] + base_stats[x] + mastery_bonus[x]), stat_maximums[x])   #respective stat caps, including mastery bonuses
		avg_gro[x] = min((avg_gro[x] + avg_pot[x] + base_stats[x] + mastery_bonus[x]), stat_maximums[x])

	m_crit = min(m_crit, max_crit) #Ensures that Critical Chance, Evasion, and
	m_eva = min(m_eva, max_eva)	   #elemental resistances have not exceeded their
	m_elem = min(m_elem, max_elem) #respective caps
	m_holy = min(m_elem, max_elem)
	m_dark = min(m_elem, max_elem)

	detail_str += '-' * 32 + (							#Generates a summary of job mastery totals
		'\nTotal Mastery Bonus:\n'						#and appends it to detail_str
		f'ATK: {m_atk}\n'
		f'DEF: {m_def}\n'
		f'MND: {m_mnd}\n'
		f'RES: {m_res}\n'
		f'SPD: {m_spd}\n'
		f'Crit: {m_crit}%\n'
		f'Evade: {m_eva}%\n'
		f'Fir/Wat/Thun/Ert resistance: {m_elem}%\n'
		f'Light resistance: {m_holy}%\n'
		f'Dark resistance: {m_dark}%\n'
		) 

	detail_str += '-' * 32 + '\nJobs Mastered:\n'		#Appends a listing of all mastered jobs
														#to detail_str
	for job in masteries:
		detail_str += f'{job}\n'

	window['JLVLS'].update(detail_str)
	stats_str = (
				f'Final Stats:\n'
				'Values are rounded to 2 decimal places.\n'
				'Average values are shown in ()\n'								#Generates a summary of final projected stat
				f'ATK: {min_gro[0]:.2f}~{max_gro[0]:.2f} ({avg_gro[0]:.2f})\n'  #growths, with values truncated to 2 decimal
				f'DEF: {min_gro[1]:.2f}~{max_gro[1]:.2f} ({avg_gro[1]:.2f})\n'  #places where required.
				f'MND: {min_gro[2]:.2f}~{max_gro[2]:.2f} ({avg_gro[2]:.2f})\n'  
				f'RES: {min_gro[3]:.2f}~{max_gro[3]:.2f} ({avg_gro[3]:.2f})\n'
				f'SPD: {min_gro[4]:.2f}~{max_gro[4]:.2f} ({avg_gro[4]:.2f})\n'
				f'HP: {min_gro[5]:.2f}~{max_gro[5]:.2f} ({avg_gro[5]:.2f})\n'
				f'MP: {min_gro[6]:.2f}~{max_gro[6]:.2f} ({avg_gro[6]:.2f})\n'
				f'Crit: {m_crit}%\n'
				f'Evasion: {m_eva}%\n'
				f'Fire resistance: {m_elem}%\n'
				f'Water resistance: {m_elem}%\n'
				f'Thunder resistance: {m_elem}%\n'
				f'Earth resistance: {m_elem}%\n'
				f'Light resistance: {m_holy}%\n'
				f'Dark resistance: {m_dark}%\n'
				)
	window['TSTATS'].update(stats_str)

def master_check_control(m_core, m_other, all_jobs, std_jobs):
	'''Function to analyze the list of mastered jobs and
	ensure that the 'Master Standard' and 'Master Everything
	checkboxes react accordingly. For example, if the user
	manually checks the 'Master Job' box for every standard
	job, the 'Master Standard' checkbox should update to also
	be checked.

	Arguments:

	m_core: List. A list of the currently mastered standard jobs.
	Standard here is defined as any job that does not belong to a
	story character, which requires a special badge to access, or
	which comes from a mod.

	m_other: List. A list of currently mastered non-standard jobs,
	i.e. those which are not in m_core.

	all_jobs: List. A list of all job names.

	std_jobs: Tuple. A tuple containing the names of all 'Standard'
	jobs. '''
	m_core.sort()
	m_other.sort()
	check_list = list(std_jobs)
	check_list.sort()
	all_masteries = m_core + m_other
	all_masteries.sort()
	all_jobs.sort()

	if m_core == check_list: 
		window['M_ALL'].update(True)
	else:
		window['M_ALL'].update(False)
	if all_masteries == all_jobs:
		window['M_EVERY'].update(True)
	else:
		window['M_EVERY'].update(False)

def info_window():
	'''Displays a window containing the authoer information
	and legal disclaimer.'''
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

def save_data(stats, details):
	'''Saves the user's job growth chart to file.

	Arguments:

	'stats': String. Should be the current value of the 'TSTATS'
	sg.Multiline object on the main window.

	'details': String. Should be the current value of the 'JLVLS'
	sg.Multiline object on the main window.

	The function will concatenate 'stats' and 'details'
	into a single formatted text string, and save it as
	a .txt file to the location of user's choice, using
	the OS standard file saving procedure.'''

	output = 'Summary of levels\n\n'+details+'\n\n'+stats 
	if file_name := sg.popup_get_file('',no_window=True,save_as=True,file_types=((('Text Files', '.txt'),))):
		try:
			with open(file_name, 'w', encoding='utf-8') as file:
				file.write(output)
		except:
			sg.popup(f'Could not save {file_name}. Ensure you have enough disk space to save the file, and that you have permission to save to the intended location.', title='Error', font=('any', 15))


try:
	with open('job_growths.dat', 'r') as file:
		job_data = json.load(file)
		jobs_list = list(job_data.keys())
		jobs_list.sort()
		for job in jobs_list:
			job_levels.update({job:0})
except FileNotFoundError:
	sg.popup('Cannot find required file: job_growths.dat. This file should have been included with your download and is required for use of the progam.'
			' Please ensure job_growths.dat is in the same folder as this program and try again.',title='Error',font=('any',15))
	exit()
except json.decoder.JSONDecodeError:
	sg.popup('The required file "job_growths.dat" has been damaged or corrupted and cannot be loaded.',title='Error',font=('any',15))
	exit()

selector = [	[sg.Combo(values=jobs_list, default_value='Select starting job...', size=17, readonly=True,enable_events=True, key='INIT_JOB', tooltip='Select the job the character will\nbe at creation/level reset.', pad=((5,6),(5,5))), sg.Push(), sg.Combo(values=jobs_list, default_value='Select job...', size=17, readonly=True,enable_events=True, tooltip='Select a job to gain levels in.', key='JOB_SEL'),sg.Push(), sg.Text('Level',size=9), sg.Multiline(char_level,size=(8,1),key='LVL',disabled=True,no_scrollbar=True)],
				[sg.Text('Base HP', size=9), sg.Multiline('',size=(6,1),key='b_hp',disabled=True,no_scrollbar=True),sg.Text('HP Gain', size=9), sg.Multiline('',size=(6,1),key='g_hp',disabled=True,no_scrollbar=True),sg.Text('Mastery HP', size=12), sg.Multiline('',size=(4,1),key='m_hp',disabled=True,no_scrollbar=True), sg.Text('Mastery Crit', size=12), sg.Multiline('',size=(4,1),key='m_crit',disabled=True,no_scrollbar=True)],
				[sg.Text('Base MP',size=9), sg.Multiline('',size=(6,1),key='b_mp',disabled=True,no_scrollbar=True),sg.Text('MP Gain',size=9), sg.Multiline('',size=(6,1),key='g_mp',disabled=True,no_scrollbar=True),sg.Text('Mastery MP', size=12), sg.Multiline('',size=(4,1),key='m_mp',disabled=True,no_scrollbar=True), sg.Text('Mastery Evade', size=12), sg.Multiline('',size=(4,1),key='m_eva',disabled=True,no_scrollbar=True)],
				[sg.Text('Base ATK', size=9), sg.Multiline('',size=(6,1),key='b_atk',disabled=True,no_scrollbar=True),sg.Text('ATK Gain', size=9), sg.Multiline('',size=(6,1),key='g_atk',disabled=True,no_scrollbar=True), sg.Text('Mastery ATK', size=12), sg.Multiline('',size=(4,1),key='m_atk',disabled=True,no_scrollbar=True), sg.Text('M. Elem Res', size=12), sg.Multiline('',size=(4,1),key='m_elem',disabled=True,no_scrollbar=True)],
				[sg.Text('Base DEF',size=9), sg.Multiline('',size=(6,1),key='b_def',disabled=True,no_scrollbar=True),sg.Text('DEF Gain',size=9), sg.Multiline('',size=(6,1),key='g_def',disabled=True,no_scrollbar=True), sg.Text('Mastery DEF', size=12), sg.Multiline('',size=(4,1),key='m_def',disabled=True,no_scrollbar=True), sg.Text('M. Light Res', size=12), sg.Multiline('',size=(4,1),key='m_holy',disabled=True,no_scrollbar=True)],
				[sg.Text('Base MND', size=9), sg.Multiline('',size=(6,1),key='b_mnd',disabled=True,no_scrollbar=True),sg.Text('MND Gain', size=9), sg.Multiline('',size=(6,1),key='g_mnd',disabled=True,no_scrollbar=True), sg.Text('Mastery MND', size=12), sg.Multiline('',size=(4,1),key='m_mnd',disabled=True,no_scrollbar=True), sg.Text('M. Dark Res', size=12), sg.Multiline('',size=(4,1),key='m_dark',disabled=True,no_scrollbar=True)],
				[sg.Text('Base RES',size=9), sg.Multiline('',size=(6,1),key='b_res',disabled=True,no_scrollbar=True),sg.Text('RES Gain',size=9), sg.Multiline('',size=(6,1),key='g_res',disabled=True,no_scrollbar=True), sg.Text('Mastery RES', size=12), sg.Multiline('',size=(4,1),key='m_res',disabled=True,no_scrollbar=True)],
				[sg.Text('Base SPD', size=9), sg.Multiline('',size=(6,1),key='b_spd',disabled=True,no_scrollbar=True),sg.Text('SPD Gain', size=9), sg.Multiline('',size=(6,1),key='g_spd',disabled=True,no_scrollbar=True), sg.Text('Mastery SPD', size=12), sg.Multiline('',size=(4,1),key='m_spd',disabled=True,no_scrollbar=True)],
				[sg.Checkbox('Master Job', key='MASTER',enable_events=True,tooltip='Select this if the current job is mastered.'), sg.Checkbox('Master Standard', key='M_ALL',enable_events=True, tooltip='Set all standard jobs as being mastered.'),
				sg.Checkbox('Master Everything', key='M_EVERY',enable_events=True,tooltip='Master every job in the job list. Note that this\ncannot happen normally without save editing.'),
				sg.Push(), sg.Button('Clear Mastery', key='CLEAR', tooltip='Clears all masteries')],
				[sg.Button('About'), sg.Button('Save'), sg.Push(), sg.Text('Levels to gain:',pad=((5,10),(5,5))),sg.Input('',size=(4,1),key='GLV',justification='right',pad=((5,72),(5,5)),enable_events=True), sg.Button('Add', size=5, tooltip='Add the specified number of levels in this job.'),
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

	if event == 'GLV':									#Ensures that the user value input in the 'GLV' field
		if len(values['GLV']) > 2: 						#is at most a valid 2-digit integer
			window['GLV'].update(values['GLV'][:2])
		if values['GLV'].isdecimal() == False:
			window['GLV'].update(''.join(list(l for l in values['GLV'] if l.isnumeric())))

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
			if job in mastered_core or job in mastered_other:
				window['MASTER'].update(True)
			else:
				window['MASTER'].update(False)

	if event == 'Add' and values['GLV'] and int(values['LVL']) < 99:
		if values['JOB_SEL'] != 'Select job...':
			g_lv = int(values['GLV'])
			job = values['JOB_SEL']
			if g_lv > 0 and g_lv <= (99 - char_level):
				job_levels[job] += g_lv
				window['LVL'].update(int(values['LVL']) + g_lv)
				char_level += g_lv
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
		master_check_control(mastered_core,mastered_other,jobs_list,std_jobs_list)

	if event == 'M_ALL':
		if values['M_ALL']:
			mastered_core = list(std_jobs_list)
		else:
			mastered_core = []
		if values['JOB_SEL'] != 'Select job...' and values['INIT_JOB'] != 'Select starting job...':
			calc_stats(values['INIT_JOB'], job_levels, mastered_core, mastered_other)
		if values['JOB_SEL'] != 'Select job...':
			job = values['JOB_SEL']
			if job in mastered_core or job in mastered_other:
				window['MASTER'].update(True)
			else:
				window['MASTER'].update(False)
		master_check_control(mastered_core,mastered_other,jobs_list,std_jobs_list)

	if event == 'M_EVERY':
		if values['M_EVERY']:
			mastered_core = list(std_jobs_list)
			mastered_other = [job for job in jobs_list if job not in std_jobs_list]
			window['M_ALL'].update(True)
		else:
			mastered_core = []
			mastered_other = []
			window['M_ALL'].update(False)
		if values['JOB_SEL'] != 'Select job...' and values['INIT_JOB'] != 'Select starting job...':
			calc_stats(values['INIT_JOB'], job_levels, mastered_core, mastered_other)
		if values['JOB_SEL'] != 'Select job...':
			job = values['JOB_SEL']
			if job in mastered_core or job in mastered_other:
				window['MASTER'].update(True)
			else:
				window['MASTER'].update(False)
		master_check_control(mastered_core,mastered_other,jobs_list,std_jobs_list)

	if event == 'CLEAR':
		mastered_core = []
		mastered_other = []
		window['MASTER'].update(False)
		window['M_ALL'].update(False)
		window['M_EVERY'].update(False)
		if values['JOB_SEL'] != 'Select job...' and values['INIT_JOB'] != 'Select starting job...':
			calc_stats(values['INIT_JOB'], job_levels, mastered_core, mastered_other)

	if event == 'Reset':
		char_level = 1
		for job in jobs_list:
			job_levels.update({job:0})
		window['INIT_JOB'].update('Select starting job...')
		window['JOB_SEL'].update('Select job...')
		window['MASTER'].update(False)							#Resets all relevant values to an initial state.
		mastered_core = []						
		mastered_other = []
		window['M_ALL'].update(False)
		window['M_EVERY'].update(False)
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

	if event=='Save':
		if values['TSTATS'] and values['JLVLS']:
			save_data(values['TSTATS'], values['JLVLS'])

window.close()