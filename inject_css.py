import os

files = ['templates/cashier.html', 'templates/manager.html', 'templates/store.html', 'templates/customer.html']
link_tag = '    <link rel="stylesheet" href="/static/css/premium.css">\n</head>'

for file in files:
    try:
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'premium.css' not in content:
            content = content.replace('</head>', link_tag)
            with open(file, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Updated {file}")
    except Exception as e:
        print(f"Error on {file}: {e}")
