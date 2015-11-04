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
    '        }' +
    '    }' +
    '}'


http = Net::HTTP.new( 'localhost', 9200 )

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


csv.each do |row|
    input = row.split(",")

    # 0        1     2     3        4              5  6   7         8
    # Kaycee,Edythe,Bode,private,Fictional Office,ZZ7,B,1066224,HELENBURY BARON
    name = {
        'title_number' => input[5],
        'office' => input[4],
        'sub_register' => input[6],
        'name_type' => input[3],
        'forenames' => input[0] + ' ' + input[1],
        'surname' => input[2],
        'full_name' => input[0] + ' ' + input[1] + ' ' + input[2]
    }

    if input[7] != '' # Data contains a complex name
        name['number'] = input[7]
        name['full_name'] = input[8]
    else
        name['number'] = nil
    end

    nameBody = name.to_json
    response = http.request( Net::HTTP::Post.new( '/index/names' ), nameBody )
end







