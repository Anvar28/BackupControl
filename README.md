# BackupControl
Программа для проверки создания архивов.
По переданным параметрам проверяет в каталоге архивов
1. Когда был создан последний архив, если дата меньше текущего дня то оправляет письмо
2. Проверяет размер архива по сравнению с прошлым архивом,  если размер меньше, то опправляет письмо
3. Проверяет существует ли каталог архива, если нет, то оправляет письмо
4. Раз в неделю отправляет письмо для проверки связи
