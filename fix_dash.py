with open("frontend/src/pages/Dashboard.tsx", "r", encoding="utf-8") as f:
    content = f.read()

bad_catch = """      } catch (e) {
        console.error("Approval failed", e);
      } finally {"""

good_catch = """      } catch (e) {
        console.error("Approval failed", e);
        alert("Approval failed or case is not in ESCALATED state.");
      } finally {"""

if bad_catch in content:
    content = content.replace(bad_catch, good_catch)
    with open("frontend/src/pages/Dashboard.tsx", "w", encoding="utf-8") as f:
        f.write(content)
    print("Fixed Dashboard catch block.")
else:
    print("Could not find Dashboard catch block.")
