# Page snapshot

```yaml
- generic [ref=e4]:
  - button "Back to Dashboard" [ref=e8] [cursor=pointer]:
    - img [ref=e10] [cursor=pointer]
    - text: Back to Dashboard
  - generic [ref=e12]:
    - generic [ref=e13]:
      - img [ref=e15]
      - heading "Create New Team" [level=1] [ref=e17]
    - paragraph [ref=e18]: Give your team a unique name to get started with collaborative project management
  - generic [ref=e22]:
    - generic [ref=e23]:
      - generic [ref=e24]: Team Name
      - generic [ref=e25]:
        - img [ref=e27]
        - textbox "Team Name" [ref=e29]
        - group:
          - generic: Team Name
    - button "Create Team" [disabled]:
      - generic:
        - img
      - text: Create Team
    - paragraph [ref=e30]: You will be automatically assigned as the team owner
```
