require 'json'
require 'net/http'
require 'uri'

dir = File.dirname(__FILE__)
csv = File.open("#{dir}/names.csv").read.split(/\r?\n/)

metaphone = '{' +
    '    "settings": {' +
    '        "analysis": {' +
    '            "filter": {' +
    '                "dbl_metaphone": {' +
    '                    "type": "phonetic",' +
    '                    "encoder": "double_metaphone"' +
    '                }' +
    '            },' +
    '            "analyzer": {' +
    '                "dbl_metaphone": {' +
    '                    "tokenizer": "standard",' +
    '                    "filter": "dbl_metaphone"' +
    '                }' +
    '            }' +
    '        }' +
    '    }' +
    '}'

# maps some fields...
mapping = '{' +
    '    "properties": {' +
    '        "surname": {' +
    '            "type": "string",' +
    '            "fields": {' +
    '                "phonetic": {' +
    '                    "type": "string",' +
    '                    "analyzer": "dbl_metaphone"' +
    '                }' +
    '            }' +
    '        },' +
    '        "forenames": {' +
    '            "type": "string",' +
    '            "fields": {' +
    '                "phonetic": {' +
    '                    "type": "string",' +
    '                    "analyzer": "dbl_metaphone"' +
    '                }' +
    '            }' +
    '        },' +
    '        "full_name": {' +
    '            "type": "string",' +
    '            "index": "not_analyzed"' +
    '        },' +
    '        "title_number": {' +
    '            "type": "string",' +
    '            "index": "not_analyzed"' +
    '        }' +
    '    }' +
    '}'


http = Net::HTTP.new( 'localhost', 9200 )
http.request( Net::HTTP::Delete.new( '/index' ) )
response = http.request(Net::HTTP::Get.new("/index/_mapping/names"))

if response.code == "404"
    puts 'Adding mapping'
    r = http.request( Net::HTTP::Put.new( '/index' ), metaphone )
    puts r.code
    puts r.body
    r = http.request( Net::HTTP::Put.new( '/index/_mapping/names' ), mapping )
    puts r.code
    puts r.body
else
    data = JSON.parse(response.body)
    forenames = data['index']['mappings']['names']['properties']['forenames']
    if forenames.key?('fields') == false
        puts 'Adding mapping to existing index'
        r = http.request( Net::HTTP::Put.new( '/index' ), metaphone )
        puts r.code
        r = http.request( Net::HTTP::Put.new( '/index/_mapping/names' ), mapping )
        puts r.code
    else
        puts 'Index exists'
    end
end