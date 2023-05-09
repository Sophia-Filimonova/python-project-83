### Hexlet tests and linter status:
[![Actions Status](https://github.com/Sophia-Filimonova/python-project-83/workflows/hexlet-check/badge.svg)](https://github.com/Sophia-Filimonova/python-project-83/actions)
[![Python CI](https://github.com/Sophia-Filimonova/python-project-83/actions/workflows/pyci.yml/badge.svg)](https://github.com/Sophia-Filimonova/python-project-83/actions/workflows/pyci.yml)
<a href="https://codeclimate.com/github/Sophia-Filimonova/python-project-83/maintainability"><img src="https://api.codeclimate.com/v1/badges/d399d851169a509b5da6/maintainability" /></a>


Domain:
https://python-project-83-production-410c.up.railway.app/

Page Analyzer – сайт, который анализирует указанные страницы на SEO-пригодность. Введите URL страницы в форму на главной странице проекта, у URL должен быть валидный адрес, он обязательный и не превышает 255 символов. В базу данных заносится нормализованная ссылка, поэтому добавление разных ссылок с одного сайта в проект не приводит к созданию новой записи в базе данных. На странице конкретного сайта можно запустить проверку, при этом выполняется запрос к нужному сайту и собирается информация о нем (содержимое тегов &lt;h1&gt;, title и аттрибута content в теге <meta name="description" content="...">). При ошибке проверки запись в таблице проверок не создаётся, и выводится флеш-сообщение 'Произошла ошибка при проверке'. В списке сайтов выводится дата и код последней проверки.