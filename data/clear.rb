require 'json'
require 'net/http'

http = Net::HTTP.new( 'localhost', 9200 )
http.request( Net::HTTP::Delete.new( '/index' ) )