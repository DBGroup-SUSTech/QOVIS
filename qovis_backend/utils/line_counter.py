def count_cleaned_log(filepath):
    with open(filepath, 'r') as f:
        lines = f.readlines()
        lines = list(filter(lambda x: '23/11/10' in x, lines))
        print(len(lines))


def count_plan_record(filepath):
    pattern = '=== Applying'
    with open(filepath, 'r') as f:
        lines = f.readlines()
        lines = list(filter(lambda x: pattern in x, lines))
        print(len(lines))


def main():
    filepath = '/Users/carl/Code/Research/QOTrace/qotrace-web/qotrace-backend/data/data6/proc/bug0-0/log.clean.txt'
    count_cleaned_log(filepath)
    count_plan_record(filepath)


if __name__ == '__main__':
    main()
