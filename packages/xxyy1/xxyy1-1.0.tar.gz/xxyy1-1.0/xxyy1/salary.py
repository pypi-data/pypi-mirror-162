"""
用于计算公司员工的薪资
"""

company = "hit"

def yearSalary(monthSalary):
  """根据传入的月薪的值，计算出年薪：月薪*12"""
  return monthSalary*12
  pass

def daySalary(monthSalary):
  """根据传入的月薪值，计算出一天的薪资，一个月按照22.5天来算"""
  return monthSalary/22.5
  pass

if __name__ == "__main__" :
  print(yearSalary(9000))