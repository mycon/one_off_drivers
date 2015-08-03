
import optparse
def print_station(id):
	print id 

def main():
	parser = optparse.OptionParser('usage %prog '+\
					'--s1 <stationID_1> --s2 <stationID_2>')
	parser.add_option('--s1', dest='sID1', type='string', \
		help='Specify which station to pull data from.')
	parser.add_option('--s2', dest='sID2', type='string', \
                help='Specify which station to pull data from.')
	(options, args) = parser.parse_args()
	stations = []
	
	stations.extend((options.sID1, options.sID2))
	print_station(stations)



		

if __name__ == '__main__':
	main()

