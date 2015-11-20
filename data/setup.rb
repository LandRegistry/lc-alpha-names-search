require 'json'
require 'net/http'
require 'uri'

dir = File.dirname(__FILE__)
csv = File.open("#{dir}/names.csv").read.split(/\r?\n/)

metaphone = '{' +
    '    "settings": {' +
    '        "analysis": {' +
    '            "analyzer": {' +
    '                "string_lowercase": {' +
    '                    "tokenizer": "keyword",' +
    '                    "filter": "lowercase"' +
    '                }' +
    '            }' +
    '        }' +
    '    }' +
    '}'

# maps some fields...
mapping = '{' +
    '    "properties": {' +
    '        "full_name": {' +
    '            "type": "string",' +
    '            "analyzer": "string_lowercase"' +
    '        },' +
    '        "title_number": {' +
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

    # 0        1     2     3        4         5          6   7         8
    #  Simon,Trett,Smith,Private,Sole,Fictional Office,ZZ201,B,  COMPLEX NAME
    name = {
        'title_number' => input[5],
        'office' => input[4],
        'sub_register' => input[6],
        'name_type' => input[2],
        'forenames' => input[0],
        'surname' => input[1],
        'full_name' => (input[0] + ' ' + input[1]).strip,
        'prop_type' => input[3]
    }

    unless input[7].nil? # Data contains a complex name
        name['full_name'] = input[7]
    end

    nameBody = name.to_json
    response = http.request( Net::HTTP::Post.new( '/index/names' ), nameBody )
end







