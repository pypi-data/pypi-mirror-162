# datedays

datedays is available on PyPI:

```console
$ pip install datedays
```

Get the list of days in the format "%Y-%m-%d"  
When we want a lot of time This library can be used for this fixed format date array

For Example:

**Get the required date quantity list, within 3 months by default**

```
import datedays

if __name__ == '__main__':
    print(datedays.getdays())
```

```
['2022-08-05', '2022-08-06', '2022-08-07', ..., '2022-11-29', '2022-11-30']
```

**Get the remaining days of the specified month,**  
**```current_date=None```If the date is empty,**  
**the current remaining days will be obtained**

```
import datedays

if __name__ == '__main__':
    print(datedays.getcurrent_days())
```

```
['2022-08-05', '2022-08-06',... '2022-08-30', '2022-08-31']
```

**Return to the next month date list (automatically cross year)**

```
import datedays

if __name__ == '__main__':
    print(datedays.getnext_days())
```
```
['2022-09-01', '2022-09-02', ... '2022-09-29', '2022-09-30']
```
