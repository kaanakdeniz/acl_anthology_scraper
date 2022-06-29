from acl.acl import ACL

def main():
    acl = ACL();
    acl_venue = acl.get_venue("ACL")
    events = acl_venue.get_all_events(2016, 2021)


if __name__ == "__main__":
    main()