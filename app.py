st.markdown("<br><hr>", unsafe_allow_html=True)
    st.markdown("""<h3 style='color: #f8fafc;'>💬 AI Follow-up Assistant</h3>""", unsafe_allow_html=True)

    st.markdown("<p style='color: #94a3b8; font-size: 0.9rem;'>Click a quick prompt or type your own question below:</p>", unsafe_allow_html=True)

    # Interactive Quick Suggestion Buttons
    col1, col2, col3 = st.columns(3)
    
    selected_quick_prompt = None
    with col1:
        if st.button("💡 Key Takeaways"):
            selected_quick_prompt = "Can you summarize the core key takeaways from this report?"
    with col2:
        if st.button("💻 Code Example"):
            selected_quick_prompt = "Provide a clean code implementation or practical example based on this research."
    with col3:
        if st.button("📐 Future Outlook"):
            selected_quick_prompt = "What is the future outlook or potential challenges mentioned in this research?"

    if not st.session_state.messages:
        st.session_state.messages.append({
            "role": "system",
            "content": f"You are an AI research assistant. Answer follow-up questions concisely based on this research report, including citation badges where relevant:\n\n{st.session_state.report_markdown}"
        })

    for message in st.session_state.messages:
        if message["role"] != "system":
            with st.chat_message(message["role"]):
                st.markdown(message["content"], unsafe_allow_html=True)

    # Handle chat input OR quick suggestion button click
    chat_prompt = st.chat_input("Ask a follow-up question about this report...")
    prompt_to_run = selected_quick_prompt if selected_quick_prompt else chat_prompt

    if prompt_to_run:
        st.session_state.messages.append({"role": "user", "content": prompt_to_run})
        with st.chat_message("user"):
            st.markdown(prompt_to_run)

        with st.spinner("Generating response..."):
            response = call_groq_llm(st.session_state.messages, doc_only_mode=doc_only_mode)

        with st.chat_message("assistant"):
            st.markdown(response, unsafe_allow_html=True)
        st.session_state.messages.append({"role": "assistant", "content": response})

        for item in st.session_state.research_history:
            if item["query"] == st.session_state.current_query:
                item["messages"] = st.session_state.messages