#!/usr/bin/env python3
"""
Interactive example showing how to use alias_manager.add_alias()
Run this script and follow the prompts to add aliases interactively.
"""

from business_alias_manager import BusinessAliasManager


def interactive_add_alias():
    # Initialize the alias manager
    alias_manager = BusinessAliasManager()

    print("🔧 Interactive Business Alias Manager")
    print("=" * 50)
    print("This tool helps you add new business aliases.")
    print("Available official business names:")

    official_names = alias_manager.get_official_names()
    for i, name in enumerate(official_names, 1):
        print(f"   {i}. {name}")

    print("\nAvailable match types:")
    print("   1. exact_matches (highest priority)")
    print("   2. partial_matches (medium priority)")

    while True:
        print("\n" + "=" * 50)

        # Get alias text
        alias_text = input(
            "Enter the alias text to match (or 'quit' to exit): "
        ).strip()
        if alias_text.lower() == "quit":
            break

        if not alias_text:
            print("❌ Alias text cannot be empty")
            continue

        # Get official business name
        print("\nSelect the official business name:")
        for i, name in enumerate(official_names, 1):
            print(f"   {i}. {name}")

        try:
            choice = int(input("Enter number (1-{}): ".format(len(official_names))))
            if choice < 1 or choice > len(official_names):
                print("❌ Invalid choice")
                continue
            business_name = official_names[choice - 1]
        except ValueError:
            print("❌ Please enter a valid number")
            continue

        # Get match type
        print("\nSelect match type:")
        print("   1. exact_matches (exact string match)")
        print("   2. partial_matches (substring match)")

        try:
            match_choice = int(input("Enter number (1-2): "))
            if match_choice == 1:
                match_type = "exact_matches"
            elif match_choice == 2:
                match_type = "partial_matches"
            else:
                print("❌ Invalid choice")
                continue
        except ValueError:
            print("❌ Please enter a valid number")
            continue

        # Add the alias
        try:
            alias_manager.add_alias(alias_text, business_name, match_type)
            print(
                f"✅ Successfully added: '{alias_text}' -> '{business_name}' ({match_type})"
            )

            # Test the new alias
            result = alias_manager.find_business_match(alias_text)
            if result:
                matched_name, match_type_result, confidence = result
                print(
                    f"✅ Test result: '{alias_text}' -> '{matched_name}' ({match_type_result}, confidence: {confidence:.2f})"
                )
            else:
                print(f"❌ Test failed: '{alias_text}' -> No match")

        except Exception as e:
            print(f"❌ Error adding alias: {e}")

        # Ask if user wants to continue
        continue_choice = input("\nAdd another alias? (y/n): ").strip().lower()
        if continue_choice not in ["y", "yes"]:
            break

    # Show final statistics
    print("\n📊 Final Configuration Statistics:")
    print("-" * 40)
    stats = alias_manager.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")

    print("\n✅ Alias management complete!")


if __name__ == "__main__":
    interactive_add_alias()
