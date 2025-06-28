# ... previous code ...

        # Resolve overlapping entities using longest-span-first approach
        ents.sort(key=lambda span: span.end_char - span.start_char, reverse=True)
        filtered_ents = []
        covered_tokens = set()
        
        for ent in ents:
            # Check if this entity overlaps with already added entities
            tokens = range(ent.start, ent.end)
            if not any(token in covered_tokens for token in tokens):
                filtered_ents.append(ent)
                covered_tokens.update(tokens)
            else:
                logger.debug(f"Skipping overlapping entity: {ent.text}")
                overlap_count += 1
        
        doc.ents = filtered_ents
        db.add(doc)
    
    # ... rest of the code ...
